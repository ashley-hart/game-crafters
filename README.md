# Game Crafters: LLMs for World Generation

## Project Topics
Semantics | Natural Language Understanding & Semantic Parsing | NLP for Creative Writing

## Project Description
This project combines large language models (LLMs) with procedural content generation (PCG) to generate 2D ASCII-based worlds. These worlds will be in the style of the original Dwarf Fortress video game released in 2006. We will implement our pipeline using Python, PyGame, ChatGPT, and Autogen. This pipeline will receive a natural language (NL) text description of a world (e.g., "I want there to be a grassy field with a rocky mountain in the top right corner") as input and output an ASCII render world onto a PyGame canvas. The LLM will parse the input into a formatted JSON file, an intermediate program will map the keys in the JSON file into terms the ASCII-world generator can recognize, and the world generator will attempt to render a world that matches what the user described. Once this basic pipeline is functional, we will integrate Autogen, allowing multiple LLMs to collaborate on the text-to-world generation task and allowing us to compare worlds generated with and without Autogen's involvement. This work will also involve NLP techniques such as semantic parsing, dependency parsing, keyword extraction, and the definition of world generation rules inspired by NL inputs. Autogen's involvement in the world generation process is our independent variable. Our dependent variable is the quality of the words. We will assess quality by examining (1) semantic accuracy –  how well the world reflects the semantics of the natural language phrase, (2) validity – whether the generated worlds arrange features logically, and (3) diversity – how varied the worlds are across multiple prompts. This work could support developers and researchers by providing a world generator for creative and practical purposes. Furthermore, this project can contribute to a successful publication in the field of PCG and expand the growing body of research where LLMs address long-standing questions about open-ended generation.

## Project Members
- Ashley Hart (Team Lead, Word Generator Developer)
- Nhat Hoang (Research Analyst)
- Lohaan Harshit (ML Specialist)
- Pranav Manglani (Pipeline Architect)
- Swetha Chintamaneni (Testing Specialist)
  
