[![Talk2BioModels](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2biomodels.yml/badge.svg)](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2biomodels.yml)
[![Talk2Cells](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2cells.yml/badge.svg)](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2cells.yml)
[![Talk2KnowledgeGraphs](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2knowledgegraphs.yml/badge.svg)](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2knowledgegraphs.yml)
[![TESTS Talk2Scholars](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2scholars.yml/badge.svg)](https://github.com/VirtualPatientEngine/AIAgents4Pharma/actions/workflows/tests_talk2scholars.yml)
![GitHub Release](https://img.shields.io/github/v/release/VirtualPatientEngine/AIAgents4Pharma)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FVirtualPatientEngine%2FAIAgents4Pharma%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![Docker Pulls](https://img.shields.io/docker/pulls/virtualpatientengine/talk2biomodels?link=https%3A%2F%2Fhub.docker.com%2Frepository%2Fdocker%2Fvirtualpatientengine%2Ftalk2biomodels%2Fgeneral)

## Introduction

Welcome to **AIAgents4Pharma** – an open-source project by [Team VPE](https://github.com/VirtualPatientEngine) that brings together AI-driven tools to help researchers and pharma interact seamlessly with complex biological data.

Our toolkit currently consists of the following agents:

- **Talk2BioModels** _(v1 released; v2 in progress)_: Engage directly with mathematical models in systems biology.
- **Talk2KnowledgeGraphs** _(v1 in progress)_: Access and explore complex biological knowledge graphs for insightful data connections.
- **Talk2Scholars** _(v1 in progress)_: Get recommendations for articles related to your choice. Download, query, and write/retrieve them to your reference manager (currently supporting Zotero).
- **Talk2Cells** _(v1 in progress)_: Query and analyze sequencing data with ease.
- **Talk2AIAgents4Pharma** _(v1 in progress)_: Converse with all the agents above (currently supports T2B and T2KG)

![AIAgents4Pharma](docs/assets/AIAgents4Pharma.png)

## Getting Started

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FVirtualPatientEngine%2FAIAgents4Pharma%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

### Installation

#### Option 1: PyPI

```bash
pip install aiagents4pharma
```

Check out the tutorials on each agent for detailed instrcutions.

#### Option 2: Docker Hub

_Both `Talk2Biomodels` and `Talk2Scholars` are now available on Docker Hub._

1. **Pull the Docker images**

   ```bash
   docker pull virtualpatientengine/talk2biomodels
   ```

   ```bash
   docker pull virtualpatientengine/talk2scholars
   ```

2. **Run the containers**

   ```bash
   docker run -d \
     --name talk2biomodels \
     -e OPENAI_API_KEY=<your_openai_api_key> \
     -e NVIDIA_API_KEY=<your_nvidia_api_key> \
     -p 8501:8501 \
     virtualpatientengine/talk2biomodels
   ```

   ```bash
   docker run -d \
     --name talk2scholars \
     -e OPENAI_API_KEY=<your_openai_api_key> \
     -e ZOTERO_API_KEY=<your_zotero_api_key> \
     -e ZOTERO_USER_ID=<your_zotero_user_id> \
     -p 8501:8501 \
     virtualpatientengine/talk2scholars
   ```

3. **Access the Web App**  
    Open your browser and go to:

   ```
   http://localhost:8501
   ```

   _You can create a free account at NVIDIA and apply for their
   free credits [here](https://build.nvidia.com/explore/discover)._

#### **Notes**

- Ensure you **replace `<your_openai_api_key>`, `<your_nvidia_api_key>`, `<your_zotero_api_key>`, and `<your_zotero_user_id>`** with your actual credentials.
- Both applications use **port `8501`**, so run them on different ports if needed:
  ```bash
  docker run -d -e OPENAI_API_KEY=<your_openai_api_key> -p 8501:8501 virtualpatientengine/talk2scholars
  ```
  Then, access it via `http://localhost:8501`.

#### Option 3: git

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VirtualPatientEngine/AIAgents4Pharma
   cd AIAgents4Pharma
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize OPENAI_API_KEY and NVIDIA_API_KEY**

   ```bash
   export OPENAI_API_KEY=....
   export NVIDIA_API_KEY=....
   ```

   _You can create a free account at NVIDIA and apply for their
   free credits [here](https://build.nvidia.com/explore/discover)._

4. **Initialize ZOTERO_API_KEY and ZOTERO_USER_ID**

   ```bash
   export ZOTERO_API_KEY=....
   export ZOTERO_USER_ID=....
   ```

5. **[Optional] Initialize LANGSMITH_API_KEY**

   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY=<your-api-key>
   ```

   _Please note that this will create a new tracing project in your Langsmith
   account with the name `T2X-xxxx`, where `X` can be `AA4P` (Main Agent),
   `B` (Biomodels), `S` (Scholars), `KG` (KnowledgeGraphs), or `C` (Cells).
   If you skip the previous step, it will default to the name `default`.
   `xxxx` will be the 4-digit ID created for the session._

6. **Launch the app:**
   ```bash
   streamlit run app/frontend/streamlit_app_<agent>.py
   ```
   _Replace <agent> with the agent name you are interested to launch._

For detailed instructions on each agent, please refer to their respective modules.

---

## Contributing

We welcome contributions to AIAgents4Pharma! Here’s how you can help:

1. **Fork the repository**
2. **Create a new branch** for your feature (`git checkout -b feat/feature-name`)
3. **Commit your changes** (`git commit -m 'feat: Add new feature'`)
4. **Push to the branch** (`git push origin feat/feature-name`)
5. **Open a pull request** and reach out to any one of us below via Discussions:

   _Note: We welcome all contributions, not just programming-related ones. Feel free to open bug reports, suggest new features, or participate as a beta tester. Your support is greatly appreciated!_

- **Talk2Biomodels/Talk2Cells**: [@gurdeep330](https://github.com/gurdeep330) [@lilijap](https://github.com/lilijap) [@dmccloskey](https://github.com/dmccloskey)
- **Talk2KnowledgeGraphs**: [@awmulyadi](https://github.com/awmulyadi) [@dmccloskey](https://github.com/dmccloskey)
- **Talk2Scholars**: [@ansh-info](https://github.com/ansh-info) [@gurdeep330](https://github.com/gurdeep330) [@dmccloskey](https://github.com/dmccloskey)

### Current Needs

- **Beta testers** for Talk2BioModels and Talk2Scholars.
- **Developers** with experience in Python and Bioinformatics and/or knowledge graphs for contributions to AIAgents4Pharma.

Feel free to reach out to us via Discussions.

Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

---

## Feedback

Questions/Bug reports/Feature requests/Comments/Suggestions? We welcome all. Please use `Isssues` or `Discussions` 😀
