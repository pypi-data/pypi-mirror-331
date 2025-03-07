# ocroy

おしろい (O-shi-ro-i)

Ocroy is a wrapper of Japanese(日本語) OCR (optical character recognition) tools.  
It allows for easy switching of tools🍰

⚠️Under developing (Currently, planning phase)

## Supported tools

* Google [Vision API](https://cloud.google.com/vision/docs)
* [Tesseract](https://tesseract-ocr.github.io/tessdoc/)

## Setup

### Google Vision API

Set up your Google Cloud project and authentication  
https://cloud.google.com/vision/docs/ocr#set-up-your-google-cloud-project-and-authentication

**Recommended**

```
% uvx --with 'ocroy[google]' ocroy google_api path/to/image --handle-document
```

Or install this library and dependencies

```
% pip install 'ocroy[google]'
```

Then Run:

```
% ocroy google_api path/to/image --handle-document
% # OR
% python -m ocroy google_api path/to/image --handle-document
% # OR
% python -m ocroy.recognizers.google_vision_api path/to/image --handle-document
```

### Tesseract

Install  
https://tesseract-ocr.github.io/tessdoc/Installation.html

Install this library and dependencies

```
% pip install 'ocroy[tesseract]'
```

Then Run:

```
% ocroy tesseract path/to/image
% # OR
% python -m ocroy tesseract path/to/image
% # OR
% python -m ocroy.recognizers.tesseract path/to/image
```
