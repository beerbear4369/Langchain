# AI Coach Model Selection

This AI Coach application supports multiple language models. You can select which model to use in two ways:

## Method 1: Interactive Menu (Default)

When you start the application, you'll see a menu allowing you to select from available models. The menu is generated from the list of models in `config.py`:

```
==================================================
AI COACH MODEL SELECTION
==================================================
Please select a model to use:
1. gpt4o -> <model_id>
2. gpt4omini -> <model_id>
3. ...
==================================================
```

Simply enter the number corresponding to your preferred model and press Enter.

The application will ask if you want to save this selection for future runs. If you select "y", your choice will be remembered the next time you start the application.

## Method 2: Configuration File

If you prefer to set your model choice without using the menu, you can create a file named `model_config.json` in the same directory as the application.

1. Find the example file `model_config.json.example` in the application directory
2. Make a copy and rename it to `model_config.json`
3. Edit the file to specify your preferred model key (see `config.py` for available keys)

Example content:

```json
{
    "model": "gpt4o"
}
```

You can use any key from the `AVAILABLE_MODELS` dictionary in `config.py`.

## Model Performance Considerations

Different models have different characteristics. Refer to your `config.py` for descriptions and available options.

Choose based on your computer's capabilities and the quality of coaching responses you need. 