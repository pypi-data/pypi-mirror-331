# Gemini Data Extractor

This tool is a prof-of-concept for extracting data from PDFs and images, using the `gemini-2.0-flash-001` LLM from Google. This model attracted a lot of attention lately due to its good performances ad affordable API prices.

It uses Google's GenAI library to interact with the model and extract data from a given document using your prompt. The extracted date is returned in JSON format.

## Installation

You can install the tool using pip:

```bash
pip install gemini-data-extractor
```

## Usage

You can use the tool by running the following command (see also "Authentication" below):

```bash
gemini-data-extractor --path path/to/your/file.pdf --prompt-text "Your prompt here"
```

The tool will return the extracted data in JSON format to the standard output. In case of a long prompt, you can save it to a file and pass the path to the file using the `--prompt-file` argument:

```bash
gemini-data-extractor --path path/to/your/file.png --prompt-file path/to/your/prompt.txt
```

## Authentication

In order to use the `gemini` API you need to authenticate either using a gemini studio API key or via the Google Cloud SDK. You can obtain a key from [Google AI Studio](https://aistudio.google.com). You can then authenticate using the `--api-key` argument or setting the `GEMINI_API_KEY` environment variable:

```bash
gemini-data-extractor --path path/to/your/file.pdf --prompt "Your prompt here" --api-key your-api-key
```

or

```bash
export GEMINI_API_KEY=your-api-key
gemini-data-extractor --path path/to/your/file.pdf --prompt "Your prompt here"
```

Alternatively, if you have a working Google Cloud Account and the Google Cloud SDK installed, you can authenticate using the `gcloud` command:

```bash
gcloud auth application-default login
```

Then you can use the tool with the options `--project-id` and `--location` (or by setting the `GCP_PROJECT_ID` and `GCP_LOCATION` environment variables):

```bash
gemini-data-extractor --path path/to/your/file.pdf --prompt "Your prompt here" --project-id your-project-id --location your-location
```

or

```bash
export GCP_PROJECT_ID=your-project-id
export GCP_LOCATION=your-location
gemini-data-extractor --path path/to/your/file.pdf --prompt "Your prompt here"
```

## License

This tool is licensed under the MIT license. You can find more information in the [LICENSE](LICENSE) file.

## Disclaimer

Gemini is a trademark of Google LLC. This project is not affiliated with Google LLC. The tool uses the GenAI library to interact with the `gemini-2.0-flash-001` LLM from Google.
 The tool is provided as-is and is not officially supported by Google LLC. Use it at your own risk.
