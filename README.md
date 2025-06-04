# thesis-gpt

This project is work-in-progress and contains code to create a RAG-based LLM app that can chat with a `PDF` doc. It uses `langchain` and `weaviate` to parse the document(s) and create a vector db.
  
## Setting Up Project

This project uses [Hatch](https://hatch.pypa.io/latest/) for environment management and dependency installation. To get started, install Hatch:

```
pip install hatch
```

Then, create the environment:

```
hatch env create
```

Activate the environment:

```bash
hatch shell
```

For more details, refer to the [Hatch documentation](https://hatch.pypa.io/latest/).

## License

`thesis-gpt` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
