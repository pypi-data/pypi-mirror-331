import time
from typing import Optional
import click
import openapi_client as client
from openapi_client import PostgresqlAssetState as AssetState
from .logger import log
from .helpers import TimeoutTracker, Uploader, download_file


def scene_from_video(
    gender: Optional[client.EnumsGender],
    name: str,
    input: str,
    api_instance_scene_video: client.CreateSceneFromVideoApi,
    api_instance_scenes: client.ScenesApi,
    uploader: Uploader,
    timeout: int,
) -> str:
    """
    Create scene from a single video tracking multiple people.
    Uses MCME openai client to create a scene from a video file.
    First creates an empty scene asset and then uploads the video file to the asset.
    Then calls the fit to video endpoint to start the process.

    :param client.EnumsGender gender: Gender of the created avatar
    :param str name: Name of the created avatar
    :param str input: Path to the video file
    :param client.CreateSceneFromVideoApi api_instance_scene_video: API instance for creating scene from video
    :param client.AvatarsApi api_instance_avatars: API instance for avatars endpoints
    :param Uploader uploader: File Uploader instance
    :param int timeout: Timeout in seconds
    :return: Asset ID of the created scene
    :rtype: str
    :raises click.ClickException: If any of the API calls fail or the processing times timed_out
    """

    asset_id = request_scene_from_video(api_instance=api_instance_scene_video)

    upload_url = request_video_upload(api_instance=api_instance_scene_video, asset_id=asset_id)

    uploader.upload(file_to_upload=input, upload_url=upload_url)

    # Fit to video
    afv_inputs = client.DocschemasDocAFVInputs(avatarname=name, gender=gender, modelVersion=None)
    try:
        api_response = api_instance_scene_video.scene_fit_to_video(asset_id=asset_id, input=afv_inputs)
    except Exception as e:
        raise click.ClickException(
            "Exception when calling CreateSceneFromVideoApi->scene_fit_to_video: %s\n" % e
        ) from e

    if api_response.data is None or api_response.data.attributes is None:
        raise click.ClickException("Fitting to video response came back empty")

    # Wait for processing to finish
    timeout_tracker = TimeoutTracker(timeout)
    afv_state = AssetState(AssetState.AWAITING_PROCESSING)
    while timeout_tracker.is_active():
        if get_processing_state(api_instance_scenes, asset_id) == AssetState.READY:
            log.info(f"Scene from video processing finished with state {AssetState(AssetState.READY).name}")
            break
        log.info(f"Scene from video processing state: {afv_state.name}")
        time.sleep(5)
    else:
        raise click.ClickException("Scene from video creation timed out.")
    return asset_id


def request_scene_from_video(api_instance: client.CreateSceneFromVideoApi) -> str:
    """Initiate scene from video creation"""
    try:
        api_response = api_instance.create_scene_from_video()
    except Exception as e:
        raise click.ClickException(
            "Exception when calling CreateSceneFromVideoApi->create_scene_from_video: %s\n" % e
        ) from e
    if api_response.data is None:
        raise click.ClickException("Initiating scene from video response came back empty")
    asset_id = str(api_response.data.id)
    log.info(f"AssetID: {asset_id}")
    return asset_id


def request_video_upload(api_instance: client.CreateSceneFromVideoApi, asset_id: str) -> str:
    """Request video upload URL for scene creation"""
    try:
        api_response = api_instance.upload_video_to_scene(asset_id=asset_id)
    except Exception as e:
        raise click.ClickException(
            "Exception when calling CreateSceneFromVideoApi->upload_video_to_scene: %s\n" % e
        ) from e

    if api_response.data is None or api_response.data.attributes is None or api_response.data.attributes.url is None:
        raise click.ClickException("Requesting video upload response came back empty")
    return str(api_response.data.attributes.url.path)


def get_processing_state(api_instance: client.ScenesApi, asset_id: str) -> AssetState:
    """List scene to retrieve its state"""
    try:
        # List one scene
        api_response = api_instance.describe_scene(asset_id=asset_id)
    except Exception as e:
        raise click.ClickException("Exception when calling ScenesApi->describe_scene: %s\n" % e) from e
    if api_response.data is None or api_response.data.attributes is None:
        raise click.ClickException("Response came back empty")
    state = api_response.data.attributes.state
    if state == AssetState.ERROR:
        raise click.ClickException("Processing finished with state ERROR")
    else:
        return AssetState(state)


def download_scene(api_instance: client.ScenesApi, asset_id: str) -> None:
    """Downloads scene."""
    try:
        # List one scene
        api_response = api_instance.describe_scene(asset_id=asset_id)
    except Exception as e:
        raise click.ClickException("Exception when calling ScenesApi->describe_scene: %s\n" % e) from e
    if (
        api_response.data is None
        or api_response.data.attributes is None
        or api_response.data.attributes.url is None
        or api_response.data.attributes.url.path is None
    ):
        raise click.ClickException("Response came back empty")
    download_url = api_response.data.attributes.url.path
    log.info("downloading_scene")
    download_file(out_filename=f"{asset_id}.mcs", download_url=download_url)
