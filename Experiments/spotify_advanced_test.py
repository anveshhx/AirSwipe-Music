from winsdk.windows.media.control import \
GlobalSystemMediaTransportControlsSessionManager as MediaManager

import asyncio

async def main():

    sessions = await MediaManager.request_async()
    current = sessions.get_current_session()

    if not current:
        print("No session")
        return

    info = await current.try_get_media_properties_async()

    print("TITLE :", info.title)
    print("ARTIST:", info.artist)

    try:
        timeline = current.get_timeline_properties()

        print("START :", timeline.start_time)
        print("END   :", timeline.end_time)
        print("POS   :", timeline.position)

    except Exception as e:
        print("Timeline Error:", e)

asyncio.run(main())