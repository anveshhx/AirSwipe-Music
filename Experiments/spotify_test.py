from winsdk.windows.media.control import \
GlobalSystemMediaTransportControlsSessionManager as MediaManager

import asyncio

async def main():

    sessions = await MediaManager.request_async()

    current = sessions.get_current_session()

    if current:

        info = await current.try_get_media_properties_async()

        print("Song:", info.title)
        print("Artist:", info.artist)

    else:
        print("No media playing")

asyncio.run(main())