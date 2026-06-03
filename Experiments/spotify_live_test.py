
from winsdk.windows.media.control import \
GlobalSystemMediaTransportControlsSessionManager as MediaManager

import asyncio
import time

async def main():

    while True:

        try:

            sessions = await MediaManager.request_async()

            current = sessions.get_current_session()

            if current:

                info = await current.try_get_media_properties_async()

                print(
                    f"Song: {info.title} | Artist: {info.artist}"
                )

            else:

                print("Nothing Playing")

        except Exception as e:

            print(e)

        time.sleep(2)

asyncio.run(main())

