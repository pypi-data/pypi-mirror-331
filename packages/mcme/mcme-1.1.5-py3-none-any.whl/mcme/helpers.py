from typing import Callable
import requests
import tomli
import os
import json
import click
import time
from datetime import datetime
import re
from openapi_client import DocschemasDocAssetResponse as AssetResponse
from openapi_client import PostgresqlAssetState as AssetState
from .logger import log


MIME_JPG = "image/jpg"
MIME_PLAIN = "text/plain"
MIME_PNG = "image/png"
MIME_VIDEO = "video/mp4"
MIME_BINARY = "application/octet-stream"
MIME_TYPES = {
    "jpg": MIME_JPG,
    "jpeg": MIME_JPG,
    "png": MIME_PNG,
    "obj": MIME_PLAIN,
    "mp4": MIME_VIDEO,
    "smpl": MIME_BINARY,
}


def load_config(config: str) -> dict[str, str]:
    """Load config"""
    with open(config, mode="rb") as conf:
        return tomli.load(conf)


class State:
    def __init__(self, keycloak_file: str) -> None:
        """Load state from a local file"""
        self.state_file: str = keycloak_file
        self.active_user: str = ""
        self.auth_tokens: dict[str, dict[str, str]] = {}
        if not os.path.exists(self.state_file):
            return
        with open(self.state_file) as state:
            state_json = json.load(state)
            self.active_user = state_json.get("active_user")
            self.auth_tokens = state_json.get("keycloak_tokens")

    def get_user_and_tokens(self, username: str) -> tuple[str, dict[str, str]]:
        """Load state from a local file"""
        user = username if username is not None else self.active_user
        if user in self.auth_tokens:
            return user, self.auth_tokens[user]
        else:
            return user, {}

    def update(self, keycloak_tokens: dict[str, str], username: str) -> None:
        """Save the generated access tokens in a local file"""
        create_parent_dir_if_not_exists(self.state_file)
        self.active_user = username
        self.auth_tokens[username] = keycloak_tokens

        with open(self.state_file, "w") as state_file:
            json.dump(self.to_dict(), state_file)

    def to_dict(self) -> dict:
        return {"active_user": self.active_user, "keycloak_tokens": self.auth_tokens}


def create_parent_dir_if_not_exists(keycloak_file: str) -> None:
    parent_dir = os.path.dirname(keycloak_file)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)


def parse_betas(ctx: click.Context, param: click.Parameter, value: str, is_smplx: bool) -> list[float]:
    """Parse betas from command line"""
    shape_params = [float(x) for x in value.strip("[").strip("]").split(",")] if value is not None else []
    if is_smplx and value is not None and len(shape_params) != 10:
        raise click.BadArgumentUsage("If supplied, shape parameters have to have exactly 10 values.")
    return shape_params


def validate_export_parameter(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Check export parameters for direct download after creation"""
    if ctx.params["download_format"] is None:
        if value is not None:
            raise click.BadOptionUsage(
                str(param.name),
                f"""Please use option --download_format if you want to download avatar. 
                Otherwise, please leave out option --{param.name}.""",
                ctx=None,
            )
    # Set pose default value if download is requested
    elif param.name == "pose" and value is None:
        return "A"
    return value


def validate_person_mode_download_format(ctx: click.Context, param: click.Parameter, value: bool) -> bool:
    """Check that download options match avatar mode"""
    if ctx.params["download_format"] == "GLB" and not value:
        raise click.BadOptionUsage(
            "download_format", "--download-format GLB is only applicable to multi-avatar mode.", ctx=ctx
        )
    if ctx.params["download_format"] is not None and ctx.params["download_format"] != "GLB" and value:
        raise click.BadOptionUsage(
            "download_format", "--download-format can only be GLB for multi-avatar mode.", ctx=ctx
        )
    return value


def download_file(out_filename: str, download_url: str) -> None:
    """Download file using presigned aws s3 url."""
    with open(out_filename, "wb") as file:
        try:
            stream = requests.get(download_url, stream=True, timeout=60)
            stream.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise click.ClickException(str(err)) from err
        for chunk in stream.iter_content(chunk_size=1024 * 1024):
            file.write(chunk)
    log.info(f"Downloaded file to {out_filename}")


def parse_asset(asset: AssetResponse) -> tuple[str, dict]:
    """Parse asset from api response and return as dict with selected attributes"""
    if (
        asset.attributes is not None
        and asset.attributes.created_at is not None
        and asset.attributes.origin is not None
        and asset.attributes.state is not None
    ):
        created_at = datetime.fromtimestamp(asset.attributes.created_at).strftime("%Y/%m/%d %H:%M:%S")
        created_from_match = re.search("(?<=\\.).*", str(asset.attributes.origin))
        created_from = created_from_match.group() if created_from_match is not None else ""
        name = asset.attributes.name
        asset_id = asset.id
        return asset.attributes.state, {
            "assetID": asset_id,
            "name": name,
            "timestamp": created_at,
            "origin": created_from,
        }
    return "", {}


def get_ready_assets(list_function: Callable, show_max_assets: int) -> list[dict]:
    """List assets that have state READY"""
    assets: list[dict] = []
    page = 1
    # iterate through pages and collect avatars with state ready until there are enough
    while len(assets) < show_max_assets:
        api_response = list_function(limit=show_max_assets * 2, page=page)
        if api_response.data is None:
            raise click.ClickException("Response came back empty")
        if len(api_response.data) == 0:
            break
        for asset_response in api_response.data:
            state, asset = parse_asset(asset_response)
            if state == AssetState.READY:
                assets.append(asset)
            if len(assets) == show_max_assets:
                break
        page += 1
    return assets


def select_asset_number(ready_assets: list[dict], headers: str, asset_entry: Callable, prompt_message: str) -> str:
    """Select asset for further action like download or motion blending"""
    # No relevant assets available for this account
    if len(ready_assets) == 0:
        raise click.ClickException("You have no relevant assets to select.")
    # Print assets available for selection
    asset_list_string = headers
    for i, asset in enumerate(ready_assets):
        asset_list_string += "-" * 120 + "\n"
        asset_list_string += asset_entry(i, asset)
    log.info(asset_list_string)
    asset_number = click.prompt(prompt_message, type=int)
    return asset_number


class TimeoutTracker(object):
    """Helper class for tracking timeout length"""

    def __init__(self, timeout_length):
        self.start_time = time.time()
        self.timeout = timeout_length

    def reset(self):
        self.start_time = time.time()

    def timed_out(self):
        return time.time() - self.start_time > self.timeout * 60

    def is_active(self):
        return not self.timed_out()


def get_timestamp():
    """Get timestamp"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


class Uploader:
    """Class for uploading files that can be mocked"""

    def upload(self, file_to_upload: str, upload_url: str) -> None:
        """Upload an image to given url"""
        content_type = MIME_TYPES[file_to_upload.split(".")[-1].lower()]
        with open(file_to_upload, "rb") as input:
            upload_response = requests.put(upload_url, data=input, headers={"Content-Type": content_type})
        upload_response.raise_for_status()


class LocalUploader:
    """Class for uploading files that can be mocked"""

    def upload(self, file_to_upload: str, upload_url: str) -> None:
        # TODO(dheid)
        # Due to time constraints and to enable debugging this is here for now
        # Make this configurable and move it back into the Uploader above
        # Should not always be the case, and only be done if we target the local mcme stack
        # See mcme/batch_create.py line 71 and replace that with Uploader() when done
        upload_url = upload_url.replace("localstack", "localhost")
        """Upload an image to given url"""
        content_type = MIME_TYPES[file_to_upload.split(".")[-1].lower()]
        with open(file_to_upload, "rb") as input:
            upload_response = requests.put(upload_url, data=input, headers={"Content-Type": content_type})
        upload_response.raise_for_status()


def get_measurements_dict(
    height,
    weight,
    bust_girth,
    ankle_girth,
    thigh_girth,
    waist_girth,
    armscye_girth,
    top_hip_girth,
    neck_base_girth,
    shoulder_length,
    lower_arm_length,
    upper_arm_length,
    inside_leg_height,
) -> dict[str, float]:
    """Helper for assembling input measurements"""
    measurements = {
        "Height": height,
        "Weight": weight,
        "Bust_girth": bust_girth,
        "Ankle_girth": ankle_girth,
        "Thigh_girth": thigh_girth,
        "Waist_girth": waist_girth,
        "Armscye_girth": armscye_girth,
        "Top_hip_girth": top_hip_girth,
        "Neck_base_girth": neck_base_girth,
        "Shoulder_length": shoulder_length,
        "Lower_arm_length": lower_arm_length,
        "Upper_arm_length": upper_arm_length,
        "Inside_leg_height": inside_leg_height,
    }
    for key, value in measurements.copy().items():
        if value is None:
            del measurements[key]
    return measurements
