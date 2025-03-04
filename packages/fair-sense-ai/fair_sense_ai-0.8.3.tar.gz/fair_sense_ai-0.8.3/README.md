

# **FairSense-AI**

Fairsense-AI is a cutting-edge, AI-driven platform designed to promote transparency, fairness, and equity by analyzing bias in textual and visual content. Built with sustainability in mind, it leverages energy-efficient AI frameworks to ensure an eco-friendly approach to tackling societal biases.

---

## **Installation and Setup**

### **Step 1: Install Fair-Sense-AI**

Install the Fair-Sense-AI package using pip:

```bash
pip install fair-sense-ai
```

---

### Example Usage Code


#### Analyze Text for Bias

```python
from fairsenseai import analyze_text_for_bias

# Example input text to analyze for bias
text_input = "Men are naturally better than women in decision-making."

# Analyze the text for bias
highlighted_text, detailed_analysis = analyze_text_for_bias(text_input, use_summarizer=True)

# Print the analysis results
print("Highlighted Text:", highlighted_text)
print("Detailed Analysis:", detailed_analysis)
```

#### Analyze Image for Bias

```python
import requests
from PIL import Image
from io import BytesIO
from IPython.display import display, HTML
from fairsenseai import analyze_image_for_bias

# URL of the image to analyze.
image_url = "https://ichef.bbci.co.uk/news/1536/cpsprodpb/BB60/production/_115786974_d6bbf591-ea18-46b9-821b-87b8f8f6006c.jpg"

# Fetch and load the image from the URL.
response = requests.get(image_url)
if response.status_code == 200:
    image = Image.open(BytesIO(response.content))
    small_image = image.copy()
    small_image.thumbnail((200, 200))

    # Display the resized image and analyze for bias.
    print("Original Image (Resized):")
    display(small_image)
    highlighted_caption, image_analysis = analyze_image_for_bias(image, use_summarizer=True)

    # Print and display analysis results.
    print("\nHighlighted Caption:\n", highlighted_caption)
    print("\nImage Analysis:\n", image_analysis)
    if highlighted_caption:
        display(HTML(highlighted_caption))
else:
    print(f"Failed to fetch the image. Status code: {response.status_code}")
```

#### Start Server with Gradio Interface

```python
from fairsenseai import start_server

if __name__ == "__main__":
    start_server()
```

### Links to Resources

- [Google Colab Notebook for FairSense AI](https://colab.research.google.com/drive/1en8JtZTAIa5MuV5OZWYNteYl95Ql9xy7?usp=sharing)
- [Google Drive Folder with Test Data Samples](https://drive.google.com/drive/folders/1WVtoLBcaQhAElRFSqn3FWdDBLBO4Nsxd?usp=sharing)

This setup includes the package information, usage examples, and references to additional resources, which should help in understanding and utilizing the FairSense AI capabilities effectively.



---

<b>Contact:</b><br>
Dr. Shaina Raza<br>
Applied ML Scientist, Responsible AI<br>
<b>Email:</b> <a href="mailto:shaina.raza@vectorinstitute.ai">shaina.raza@vectorinstitute.ai</a>, <a href="mailto:shaina.raza@torontomu.ca">shaina.raza@torontomu.ca</a>


---

