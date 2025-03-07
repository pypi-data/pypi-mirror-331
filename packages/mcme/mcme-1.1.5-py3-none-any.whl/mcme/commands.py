import functools
import os
from typing import Any, Optional, OrderedDict

from keycloak import KeycloakOpenID
import openapi_client as client
import click
from os import path
from .logger import log
from .auth import authenticate
from .helpers import (
    load_config,
    parse_betas,
    validate_export_parameter,
    validate_person_mode_download_format,
    download_file,
    select_asset_number,
    get_timestamp,
    get_measurements_dict,
    Uploader,
    State,
    get_ready_assets,
)
from .motions import TMRMotion
from .avatars import (
    from_betas,
    export,
    from_images,
    from_measurements,
    from_scans,
    from_video,
    from_smpl,
    blend_motions,
)
from .scenes import scene_from_video, download_scene
from .user import request_user_info
from .schemas import ExportParameters
from functools import partial


CURRENT_DIR = path.dirname(path.abspath(__file__))
DEFAULT_CONFIG = path.join(CURRENT_DIR, "../configs/prod.toml")


class CustomOption(click.Option):
    """Custom option class that adds the attribute help_group to the option"""

    def __init__(self, *args, **kwargs):
        self.help_group = kwargs.pop("help_group", None)
        super().__init__(*args, **kwargs)


class CustomCommand(click.Command):
    def format_options(self, ctx, formatter):
        """Writes options into the help text."""
        opts = OrderedDict([("Options", [])])
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, "help_group"):
                    opts.setdefault(param.help_group, []).append(rv)
                else:
                    opts["Options"].append(rv)

        for help_group, param in opts.items():
            with formatter.section(help_group):
                formatter.write_dl(param)


def avatar_download_format(func):
    @click.option(
        "--download-format",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Choice(["OBJ", "FBX"], case_sensitive=False),
        is_eager=True,
        help="Format for downloading avatar.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def avatar_scene_download_format(func):
    @click.option(
        "--download-format",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Choice(["OBJ", "FBX", "GLB"], case_sensitive=False),
        is_eager=True,
        help="Format for downloading avatar. GLB is only applicable to multi-avatar/scene mode.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def avatar_download_params(func):
    @click.option(
        "--pose",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Choice(["T", "A", "I", "SCAN"], case_sensitive=False),
        callback=validate_export_parameter,
        help="""Pose the downloaded avatar should be in. SCAN is not applicable for avatars created from betas or 
        measurements since it corresponds to a captured pose or motion.""",
    )
    @click.option(
        "--animation",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Choice(["a-salsa"], case_sensitive=False),
        callback=validate_export_parameter,
        help="Animation for the downloaded avatar",
    )
    @click.option(
        "--compatibility-mode",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Choice(["DEFAULT", "OPTITEX", "UNREAL"], case_sensitive=False),
        callback=validate_export_parameter,
        help="Adjust output for compatibility with selected software.",
    )
    @click.option(
        "--out-file",
        cls=CustomOption,
        help_group="Avatar download options",
        type=click.Path(dir_okay=False),
        callback=validate_export_parameter,
        help="File to save created avatar mesh to",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
@click.option(
    "--config",
    type=click.Path(exists=True),
    default=os.environ.get("MCME_CONFIG_PATH", DEFAULT_CONFIG),
    help="Path to config file",
)
@click.option("--username", default=lambda: os.environ.get("MCME_USERNAME"))
@click.option("--password", default=lambda: os.environ.get("MCME_PASSWORD"))
def cli(ctx: click.Context, username: str, password: str, config: str) -> None:
    """
    Command-line interface for the Meshcapade.me API.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)
    ctx.obj["keycloak_tokens"] = os.path.expanduser(ctx.obj["config"]["cli_state"]["keycloak_tokens"])
    auth_config = ctx.obj["config"]["auth"]
    keycloak_openid: KeycloakOpenID = KeycloakOpenID(
        server_url=auth_config["server_url"], client_id=auth_config["client_id"], realm_name=auth_config["realm_name"]
    )
    state = State(ctx.obj["keycloak_tokens"])
    ctx.obj["token"] = authenticate(keycloak_openid, state, username, password)
    # construct api client
    configuration = client.Configuration(host=ctx.obj["config"]["api"]["host"])
    configuration.access_token = ctx.obj["token"]
    # Enter a context with an instance of the API client
    ctx.obj["api_client"] = client.ApiClient(configuration)


@cli.result_callback()
@click.pass_context
def close_api_client(ctx: click.Context, result: Any, **kwargs):
    ctx.obj["api_client"].close()


@cli.group()
@click.pass_context
def create(ctx: click.Context) -> None:
    """
    Create avatars or scenes. Please be aware that these commands cost credits.
    """
    # all create avatar operations need keycloak authentication


@create.command(cls=CustomCommand, name="from-betas")
@click.pass_context
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    help="Gender of created avatar",
)
@click.option(
    "--betas",
    type=click.UNPROCESSED,
    callback=partial(parse_betas, is_smplx=False),
    help='Beta values. Supply like 0.1,0.2 or "[0.1,0.2]"',
)
@click.option("--name", type=str, default="avatar_from_betas", help="Name of created avatar")
@click.option(
    "--model-version",
    type=click.Choice(client.EnumsModelVersion.enum_values(), case_sensitive=False),
    help="Model version",
)
@avatar_download_format
@avatar_download_params
def create_from_betas(
    ctx: click.Context,
    gender: Optional[client.EnumsGender],
    betas: list[float],
    name: str,
    model_version: Optional[client.EnumsModelVersion],
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar from betas."""
    api_instance = client.CreateAvatarsFromBetasApi(ctx.obj["api_client"])
    asset_id = from_betas(gender, betas, name, model_version, api_instance)
    log.info(f"AssetID: {asset_id}")

    # Exit here if avatar should not be downloaded
    if download_format:
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        download_avatar(ctx=ctx, params=params, asset_id=asset_id)


@create.command(cls=CustomCommand, name="from-measurements")
@click.pass_context
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    required=True,
    help="Gender of created avatar",
)
@click.option("--name", type=str, default="avatar_from_measurements", help="Name of created avatar")
@click.option("--height", type=float, help="Height")
@click.option("--weight", type=float, help="Weight")
@click.option("--bust-girth", type=float, help="Bust girth")
@click.option("--ankle-girth", type=float, help="Ankle girth")
@click.option("--thigh-girth", type=float, help="Thigh girth")
@click.option("--waist-girth", type=float, help="Waist girth")
@click.option("--armscye-girth", type=float, help="Armscye girth")
@click.option("--top-hip-girth", type=float, help="Top hip girth")
@click.option("--neck-base-girth", type=float, help="Neck base girth")
@click.option("--shoulder-length", type=float, help="Shoulder length")
@click.option("--lower-arm-length", type=float, help="Lower arm length")
@click.option("--upper-arm-length", type=float, help="Upper arm length")
@click.option("--inside-leg-height", type=float, help="Inside leg height")
@click.option(
    "--model-version",
    type=click.Choice(client.EnumsModelVersion.enum_values(), case_sensitive=False),
    help="Model version",
)
@avatar_download_format
@avatar_download_params
def create_from_measurements(
    ctx: click.Context,
    gender: Optional[client.EnumsGender],
    name: str,
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
    model_version: Optional[client.EnumsModelVersion],
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar from measurements."""
    # Create avatar from measurements
    measurements = get_measurements_dict(
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
    )
    api_instance_from_measurements = client.CreateAvatarFromMeasurementsApi(ctx.obj["api_client"])
    api_instance_avatars = client.AvatarsApi(ctx.obj["api_client"])
    timeout = ctx.obj["config"]["cli"]["timeout"]
    asset_id = from_measurements(
        gender, name, measurements, model_version, api_instance_from_measurements, api_instance_avatars, timeout
    )

    # Exit here if avatar should not be downloaded
    if download_format:
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        download_avatar(ctx=ctx, params=params, asset_id=asset_id)


@create.command(cls=CustomCommand, name="from-images")
@click.pass_context
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    help="Gender of created avatar",
)
@click.option("--name", type=str, default="avatar_from_images", help="Name of created avatar")
@click.option("--input", type=click.Path(dir_okay=False, exists=True), help="Path to input image")
@click.option("--height", type=int, help="Height of the person in the image")
@click.option("--weight", type=int, help="Weight of the person in the image")
@click.option(
    "--image-mode",
    type=click.Choice(["AFI", "BEDLAM_CLIFF"], case_sensitive=False),
    default="AFI",
    help="Mode for avatar creation",
)
@avatar_download_format
@avatar_download_params
def create_from_images(
    ctx: click.Context,
    gender: Optional[client.EnumsGender],
    name: str,
    input: str,
    height: int,
    weight: int,
    image_mode: str,
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar from images."""
    api_instance_images = client.CreateAvatarFromImagesApi(ctx.obj["api_client"])
    api_instance_avatars = client.AvatarsApi(ctx.obj["api_client"])
    uploader = Uploader()
    timeout = ctx.obj["config"]["cli"]["timeout"]
    asset_id = from_images(
        gender, name, input, height, weight, image_mode, api_instance_images, api_instance_avatars, uploader, timeout
    )

    # Exit here if avatar should not be downloaded
    if download_format:
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        download_avatar(ctx=ctx, params=params, asset_id=asset_id)


@create.command(cls=CustomCommand, name="from-scans")
@click.pass_context
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    help="Gender of created avatar",
)
@click.option("--name", type=str, default="avatar_from_scans", help="Name of created avatar")
@click.option("--input", type=click.Path(dir_okay=False, exists=True), help="Path to input image")
@click.option("--init-pose", type=str, help="Pose for initialization")
@click.option("--up-axis", type=str, help="Up axis")
@click.option("--look-axis", type=str, help="Look axis")
@click.option("--input-units", type=str, help="Input units of scan")
@avatar_download_format
@avatar_download_params
def create_from_scans(
    ctx: click.Context,
    gender: Optional[client.EnumsGender],
    name: str,
    input: str,
    init_pose: str,
    up_axis: str,
    look_axis: str,
    input_units: str,
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar from scans."""
    api_instance_scan = client.CreateAvatarFromScansApi(ctx.obj["api_client"])
    api_instance_avatars = client.AvatarsApi(ctx.obj["api_client"])
    uploader = Uploader()
    timeout = ctx.obj["config"]["cli"]["timeout"]
    asset_id = from_scans(
        gender,
        name,
        input,
        init_pose,
        up_axis,
        look_axis,
        input_units,
        api_instance_scan,
        api_instance_avatars,
        uploader,
        timeout,
    )

    # Exit here if avatar should not be downloaded
    if download_format:
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        download_avatar(ctx=ctx, params=params, asset_id=asset_id)


@create.command(cls=CustomCommand, name="from-video")
@click.pass_context
@click.option(
    "--multi-person/--single-person",
    default=False,
    callback=validate_person_mode_download_format,
    help="Specify --multi-person to produce a scene with multiple avatars. "
    "Option --single-person is the default and produces a single avatar.",
)
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    help="Gender of created avatar",
)
@click.option("--name", type=str, default="avatar_from_video", help="Name of created avatar")
@click.option("--input", type=click.Path(dir_okay=False, exists=True), required=True, help="Path to input video")
@avatar_scene_download_format
@avatar_download_params
def create_from_video(
    ctx: click.Context,
    multi_person: bool,
    gender: Optional[client.EnumsGender],
    name: str,
    input: str,
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create scene or avatar from a single video. To create a scene with multiple avatars,
    use mcme create from-video --multi-person."""
    uploader = Uploader()
    timeout = ctx.obj["config"]["cli"]["timeout"]
    api_instance_video: client.CreateAvatarFromVideoApi | client.CreateSceneFromVideoApi
    api_instance_asset: client.AvatarsApi | client.ScenesApi
    if not multi_person:
        # Create single avatar
        api_instance_video = client.CreateAvatarFromVideoApi(ctx.obj["api_client"])
        api_instance_asset = client.AvatarsApi(ctx.obj["api_client"])
        asset_id = from_video(gender, name, input, api_instance_video, api_instance_asset, uploader, timeout)
        # Exit here if avatar should not be downloaded
        if download_format:
            params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
            download_avatar(ctx=ctx, params=params, asset_id=asset_id)
    else:
        # Create scene
        api_instance_video = client.CreateSceneFromVideoApi(ctx.obj["api_client"])
        api_instance_asset = client.ScenesApi(ctx.obj["api_client"])
        asset_id = scene_from_video(gender, name, input, api_instance_video, api_instance_asset, uploader, timeout)
        if download_format:
            download_scene(api_instance=api_instance_asset, asset_id=asset_id)


@create.command(cls=CustomCommand, name="from-text")
@click.pass_context
@click.option("--prompt", type=str, required=True, help="Text prompt describing desired motion")
@click.option("--name", type=str, help="Name of created avatar")
@avatar_download_format
@avatar_download_params
def create_from_text(
    ctx: click.Context,
    prompt: str,
    name: str,
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar with motion from text prompt."""
    api_instance_motions = client.SearchMotionsApi(ctx.obj["api_client"])
    api_instance_avatars = client.AvatarsApi(ctx.obj["api_client"])
    timeout = ctx.obj["config"]["cli"]["timeout"]

    if name is None:
        name = prompt.replace(" ", "_")

    motion = TMRMotion(prompt)

    # Search for motion by prompt and save temporary smpl file
    motion.find_motion(api_instance_motions)

    trimmed_motion = motion.trim()

    # Use found and trimmed motion .smpl file to create avatar
    uploader = Uploader()
    asset_id = from_smpl(trimmed_motion, api_instance_avatars, name, uploader, timeout)

    # Delete temporary motion .smpl file
    motion.cleanup()

    # Exit here if avatar should not be downloaded
    if download_format:
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        download_avatar(ctx=ctx, params=params, asset_id=asset_id)


@create.command(cls=CustomCommand, name="blend-motions")
@click.pass_context
@click.option(
    "--source-avatar-id", type=str, help="A clone of this avatar will be used to attach the resulting motion to"
)
@click.option("--motion-id-1", type=str, help="First motion to use for blending")
@click.option("--motion-id-2", type=str, help="Second motion to use for blending")
@click.option(
    "--shape-parameters",
    type=click.UNPROCESSED,
    callback=partial(parse_betas, is_smplx=True),
    help='''If source-avatar-id is not specified, these SMPLX shape parameters will be used to create avatar from. 
    Supply like 0.1,0.2 or "[0.1,0.2]"''',
)
@click.option(
    "--gender",
    type=click.Choice(client.EnumsGender.enum_values(), case_sensitive=False),
    help="If source-avatar-id is not specified, this gender will be used for created avatar.",
)
@click.option("--name", type=str, default="avatar_from_blend_motion", help="Name of created avatar")
@avatar_download_format
@avatar_download_params
def create_blend_motions(
    ctx: click.Context,
    source_avatar_id: str,
    motion_id_1: str,
    motion_id_2: str,
    shape_parameters: Optional[list[float]],
    gender: Optional[client.EnumsGender],
    name: str,
    download_format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
) -> None:
    """Create avatar with blended motion attached."""
    api_instance = client.BlendMotionsApi(ctx.obj["api_client"])
    motions_api_instance = client.MotionsApi(ctx.obj["api_client"])
    avatar_api_instance = client.AvatarsApi(ctx.obj["api_client"])
    if shape_parameters == []:
        shape_parameters = None
    timeout = ctx.obj["config"]["cli"]["timeout"]
    ready_assets = get_ready_assets(list_function=motions_api_instance.list_motions, show_max_assets=10)
    select_motion_number = partial(
        select_asset_number,
        ready_assets=ready_assets,
        headers="\n\n{:<8}{:<40}{:<20}{:<20}\n".format("Number", "Asset ID", "Created from", "Timestamp"),
        asset_entry=lambda i, motion: "{:<8}{:<40}{:<20}{:<20}\n".format(
            i, motion["assetID"], motion["origin"], motion["timestamp"]
        ),
    )
    if motion_id_1 is None:
        first_motion = select_motion_number(prompt_message="Select first motion")
        motion_id_1 = ready_assets[first_motion]["assetID"]
    if motion_id_2 is None:
        second_motion = select_motion_number(prompt_message="Select second motion")
        motion_id_2 = ready_assets[second_motion]["assetID"]

    asset_id = blend_motions(
        source_avatar_id,
        motion_id_1,
        motion_id_2,
        shape_parameters,
        gender,
        name,
        api_instance,
        avatar_api_instance,
        timeout,
    )
    log.info(f"AssetID: {asset_id}")

    # Exit here if avatar should not be downloaded
    if ctx.obj["download"]:
        # Get download parameters from parent context
        params = ExportParameters(download_format, pose, animation, compatibility_mode, out_file)
        if params.download_format != "FBX" or params.pose != "SCAN":
            raise click.BadArgumentUsage(
                """Dowwnload format has to be FBX and pose has to be SCAN 
                to attach blended motion to the resulting avatar."""
            )
        # Export avatar
        ctx.invoke(
            export_and_download_avatar,
            format=params.download_format,
            pose=params.pose,
            animation=params.animation,
            compatibility_mode=params.compatibility_mode,
            out_file=params.out_file,
            asset_id=asset_id,
        )


# TODO: reimplement batch processing


def download_avatar(ctx: click.Context, params: ExportParameters, asset_id: str) -> None:
    # Export avatar
    ctx.invoke(
        export_and_download_avatar,
        format=params.download_format,
        pose=params.pose,
        animation=params.animation,
        compatibility_mode=params.compatibility_mode,
        out_file=params.out_file,
        asset_id=asset_id,
    )


@cli.command(name="download")
@click.pass_context
@click.option(
    "--format",
    type=click.Choice(["OBJ", "FBX"], case_sensitive=False),
    default="OBJ",
    help="Format for downloading avatar",
)
@click.option(
    "--pose",
    type=click.Choice(["T", "A", "SCAN", "U", "I", "W"], case_sensitive=False),
    default="A",
    help="Pose the downloaded avatar should be in",
)
@click.option(
    "--animation", type=click.Choice(["a-salsa"], case_sensitive=False), help="Animation for the downloaded avatar"
)
@click.option(
    "--compatibility-mode",
    type=click.Choice(["DEFAULT", "OPTITEX", "UNREAL"], case_sensitive=False),
    help="Compatibility mode",
)
@click.option("--out-file", type=click.Path(dir_okay=False), help="File to save created avatar mesh to")
@click.option("--asset-id", type=str, help="Asset id of avatar to be downloaded")
@click.option(
    "--show-max-avatars",
    type=int,
    default=10,
    help="Maximum number of created avatars to show (most recent ones are shown first)",
)
def export_and_download_avatar(
    ctx: click.Context,
    format: str,
    pose: str,
    animation: str,
    compatibility_mode: str,
    out_file: click.Path,
    asset_id: str,
    show_max_avatars: int,
) -> None:
    """
    Export avatar using asset id.
    """
    api_instance = client.AvatarsApi(ctx.obj["api_client"])
    name = None
    # show avatar selection dialogue if asset id is not supplied
    if asset_id is None:
        ready_assets = get_ready_assets(list_function=api_instance.list_avatars, show_max_assets=show_max_avatars)
        asset_number = select_asset_number(
            ready_assets=ready_assets,
            headers="\n\n{:<8}{:<30}{:<40}{:<20}{:<20}\n".format(
                "Number", "Name", "Asset ID", "Created from", "Timestamp"
            ),
            asset_entry=lambda i, avatar: "{:<8}{:<30}{:<40}{:<20}{:<20}\n".format(
                i, avatar["name"], avatar["assetID"], avatar["origin"], avatar["timestamp"]
            ),
            prompt_message="Number of avatar to download",
        )
        asset_id, name = ready_assets[asset_number]["assetID"], ready_assets[asset_number]["name"]

    # Export avatar
    timeout = ctx.obj["config"]["cli"]["timeout"]
    download_url = export(asset_id, format, pose, animation, compatibility_mode, api_instance, timeout)
    out_filename = (
        str(out_file)
        if out_file is not None
        else f"{get_timestamp()}_{name}.{format.lower()}"
        if (name is not None and name != "")
        else f"{get_timestamp()}_{asset_id}.{format.lower()}"
    )
    download_file(out_filename, download_url)


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show API info."""
    # Create an instance of the API class
    api_instance = client.InfoApi(ctx.obj["api_client"])

    try:
        # Show API info
        api_response: str = api_instance.info()
        log.info(api_response)
    except Exception as e:
        log.info("Exception when calling InfoApi->info: %s\n" % e)


@cli.command(name="user-info")
@click.pass_context
def user_info(ctx: click.Context) -> None:
    """Show username and available credits."""
    api_instance_user = client.UserApi(ctx.obj["api_client"])

    user = request_user_info(api_instance_user)

    log.info(f"Username: {user.email}")
    log.info(f"Credits: {user.credits}")


@cli.command(name="set-auth-token", short_help="Coming soon: Set auth token from me.meshcapade.com")
@click.pass_context
@click.option("--username", default=lambda: os.environ.get("MCME_USERNAME"))
@click.option("--token", type=str)
def set_auth_token(ctx: click.Context, username, token) -> None:
    """Coming soon: Set auth token retrieved from me.meshcapade.com to authenticate without password."""
    log.info("This functionality is coming soon, for now please authenticate with your username and password.")
