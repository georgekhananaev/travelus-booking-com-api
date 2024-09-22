import asyncio
from deep_translator import GoogleTranslator


# Define an async function to handle translation with error handling
async def async_translate(text, source_lang="en", target_lang="es"):
    try:
        # Run the blocking translation in a separate thread
        translation = await asyncio.to_thread(
            GoogleTranslator(source=source_lang, target=target_lang).translate,
            text
        )
        return translation
    except Exception as e:
        # Log the error (you can replace this with a logger if needed)
        print(f"Translation error for {target_lang}: {e}")
        # Return the original text in case of an error
        return text
