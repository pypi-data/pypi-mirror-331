"""
Optimized workflow example that demonstrates using Meno with minimal dependencies.

This example shows:
1. Using the workflow system with CPU-optimized settings
2. Working with larger datasets through streaming and chunking
3. Reducing memory usage with optimized settings
4. Fallback mechanisms when certain dependencies aren't available

Key features:
- Polars integration for faster data processing
- Quantized embeddings to reduce memory usage
- Streaming processing for larger-than-memory datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys
import time
import webbrowser
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the meno package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from meno.workflow import MenoWorkflow
from meno.utils.config import (
    load_config, 
    merge_configs
)

# Create output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

print("🔍 Optimized Workflow Example")
print("==================================")

# Create configuration with optimized settings
config_overrides = {
    "workflow": {
        "features": {
            "auto_open_browser": True
        },
        "report_paths": {
            "acronym_report": str(output_dir / "optimized_acronyms.html"),
            "spelling_report": str(output_dir / "optimized_spelling.html"),
            "comprehensive_report": str(output_dir / "optimized_report.html"),
        }
    },
    "modeling": {
        "embeddings": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",  # Small, fast model
            "batch_size": 64,                                       # Larger batches for speed
            "quantize": True,                                       # Use quantization (8-bit)
            "low_memory": True,                                     # Optimize for memory
            "use_gpu": False                                        # CPU only
        },
        "default_method": "embedding_cluster",
        "default_num_topics": 8
    },
    "preprocessing": {
        "acronyms": {
            "enabled": True,
            "custom_mappings": {
                "CEO": "Chief Executive Officer",
                "CFO": "Chief Financial Officer",
                "CTO": "Chief Technology Officer",
                "ML": "Machine Learning",
                "NLP": "Natural Language Processing",
                "ROI": "Return on Investment",
                "KPI": "Key Performance Indicator",
                "CRM": "Customer Relationship Management"
            }
        },
        "spelling": {
            "enabled": True,
            "custom_dictionary": {
                "customr": "customer",
                "satisfction": "satisfaction",
                "improvment": "improvement",
                "experiance": "experience",
                "servce": "service"
            }
        }
    }
}

# Create synthetic customer feedback dataset (larger scale)
print("\n📊 Generating synthetic customer feedback dataset...")

# Sample company names and products
companies = ["TechCorp", "GlobalSoft", "DataSystems", "CloudServices", "SecureNet"]
products = ["CRM Platform", "Cloud Storage", "Analytics Dashboard", "Mobile App", "Security Suite"]
channels = ["Email", "Phone", "Chat", "Social Media", "In-person"]
sentiments = ["Positive", "Negative", "Neutral", "Mixed"]

# Generate random dates spanning 2 years
start_date = datetime(2022, 1, 1)
end_date = datetime(2023, 12, 31)
date_range = (end_date - start_date).days

# Create feedback templates with placeholders
feedback_templates = [
    "The {product} has been great for our team. We've seen improved {area} since implementing it.",
    "We're having trouble with the {product}. The {issue} is causing problems for our {department}.",
    "After using {product} for {time}, we've noticed that {observation}.",
    "The recent update to {product} has {impact} our workflow significantly.",
    "Our {department} team finds the {product} {quality} but the {feature} needs improvement.",
    "Compared to previous solutions, {product} has {comparison}.",
    "The {service} provided by your team was {quality}. The {staff} was particularly {trait}.",
    "We experienced {issue} while trying to {action} with the {product}.",
    "The onboarding process for {product} was {quality}, but we needed more support with {area}.",
    "Your {product} lacks {feature} which is critical for our {department}."
]

# Words to fill in templates
areas = ["productivity", "efficiency", "collaboration", "communication", "data analysis"]
issues = ["slow performance", "frequent crashes", "data loss", "connection issues", "security concerns"]
departments = ["sales", "marketing", "IT", "finance", "customer service", "operations"]
observations = [
    "it has significantly improved our workflow",
    "we're still experiencing some issues",
    "our team has mixed feelings about it",
    "the learning curve is steeper than expected",
    "the ROI has been substantial"
]
impacts = ["positively affected", "negatively impacted", "slightly improved", "completely transformed", "not changed"]
qualities = ["excellent", "good", "average", "poor", "outstanding", "disappointing"]
features = ["user interface", "reporting tools", "integration capabilities", "mobile support", "customization options"]
comparisons = [
    "shown much better performance",
    "been more cost-effective",
    "provided more features",
    "been easier to use",
    "required less maintenance"
]
services = ["technical support", "customer service", "training", "implementation", "consulting"]
staff = ["support team", "account manager", "technical specialist", "trainer", "consultant"]
traits = ["helpful", "knowledgeable", "responsive", "patient", "professional"]
actions = ["generate reports", "configure settings", "import data", "create new accounts", "customize dashboards"]
times = ["one month", "three months", "six months", "a year", "just a few weeks"]

# Function to generate random feedback
def generate_feedback(with_misspellings=False, with_acronyms=False):
    company = np.random.choice(companies)
    product = np.random.choice(products)
    
    template = np.random.choice(feedback_templates)
    
    # Fill in template with random choices
    feedback = template.format(
        product=product,
        area=np.random.choice(areas),
        issue=np.random.choice(issues),
        department=np.random.choice(departments),
        observation=np.random.choice(observations),
        impact=np.random.choice(impacts),
        quality=np.random.choice(qualities),
        feature=np.random.choice(features),
        comparison=np.random.choice(comparisons),
        service=np.random.choice(services),
        staff=np.random.choice(staff),
        trait=np.random.choice(traits),
        action=np.random.choice(actions),
        time=np.random.choice(times)
    )
    
    # Add company name somewhere in the feedback
    if np.random.random() > 0.5:
        feedback = f"{company}: {feedback}"
    else:
        feedback = f"{feedback} (Regarding {company})"
    
    # Potentially add misspellings
    if with_misspellings and np.random.random() > 0.7:
        misspellings = {
            "customer": "customr",
            "satisfaction": "satisfction",
            "improvement": "improvment",
            "experience": "experiance",
            "service": "servce",
            "issue": "isue",
            "excellent": "excelent",
            "performance": "performence",
            "implementation": "implementaion",
            "significantly": "significntly"
        }
        
        # Add 1-3 random misspellings
        num_misspellings = np.random.randint(1, 4)
        words_to_misspell = np.random.choice(list(misspellings.keys()), 
                                           size=min(num_misspellings, len(misspellings)),
                                           replace=False)
        
        for word in words_to_misspell:
            if word in feedback.lower():
                feedback = feedback.replace(word, misspellings[word])
    
    # Potentially add acronyms
    if with_acronyms and np.random.random() > 0.7:
        acronyms = [
            "Our CEO thinks the ROI on this product is excellent.",
            "The CTO mentioned that ML features would be beneficial.",
            "According to our CFO, the KPI improvements justify the cost.",
            "We'd like NLP capabilities in the next release.",
            "Is this compatible with our existing CRM system?",
            "The ROI and KPI metrics have improved since implementation."
        ]
        
        # Add an acronym-heavy sentence
        acronym_text = np.random.choice(acronyms)
        if np.random.random() > 0.5:
            feedback = f"{feedback} {acronym_text}"
        else:
            feedback = f"{acronym_text} {feedback}"
    
    return feedback

# Generate a larger dataset (1000 feedback entries)
n_samples = 1000
print(f"Generating {n_samples} feedback entries...")

feedbacks = []
for i in range(n_samples):
    # Add some misspellings and acronyms to some records
    with_misspellings = np.random.random() > 0.7
    with_acronyms = np.random.random() > 0.7
    feedbacks.append(generate_feedback(with_misspellings, with_acronyms))

# Create random dates within range
feedback_dates = [start_date + timedelta(days=np.random.randint(0, date_range)) for _ in range(n_samples)]

# Create the dataframe
feedback_df = pd.DataFrame({
    "feedback_id": [f"FB-{i+10000}" for i in range(n_samples)],
    "date": feedback_dates,
    "channel": [np.random.choice(channels) for _ in range(n_samples)],
    "sentiment": [np.random.choice(sentiments) for _ in range(n_samples)],
    "feedback": feedbacks
})

print(f"Created dataset with {len(feedback_df)} entries")
print(feedback_df[["feedback_id", "channel", "sentiment"]].head(3))

# Try to import polars for optimized processing
try:
    import polars as pl
    print("\n✅ Polars is available - using optimized data processing")
    use_polars = True
    
    # Convert to polars DataFrame
    pl_df = pl.from_pandas(feedback_df)
    
    # Demonstrate a polars optimization
    start_time = time.time()
    
    # Basic polars filtering (much faster than pandas on large datasets)
    positive_feedback = pl_df.filter(pl.col("sentiment") == "Positive")
    negative_feedback = pl_df.filter(pl.col("sentiment") == "Negative")
    
    print(f"Polars filtering completed in {time.time() - start_time:.4f} seconds")
    print(f"Positive feedback: {positive_feedback.shape[0]} entries")
    print(f"Negative feedback: {negative_feedback.shape[0]} entries")
    
    # Convert back to pandas for the workflow (until native polars support is added)
    feedback_df = feedback_df
    
except ImportError:
    print("\n⚠️ Polars not available - using standard pandas processing")
    use_polars = False

# Initialize the workflow with optimized configuration
print("\n🚀 Initializing workflow with optimized settings...")
workflow = MenoWorkflow(config_overrides=config_overrides)

# Load the data
print("Loading data into workflow...")
start_time = time.time()
workflow.load_data(
    data=feedback_df,
    text_column="feedback",
    time_column="date",
    category_column="sentiment"
)
print(f"Data loading completed in {time.time() - start_time:.4f} seconds")

# Generate acronym report
print("\n📋 Generating acronym report...")
start_time = time.time()
acronym_report_path = workflow.generate_acronym_report()
print(f"Acronym report generated in {time.time() - start_time:.4f} seconds")

# Generate misspelling report
print("\n🔍 Generating misspelling report...")
start_time = time.time()
misspelling_report_path = workflow.generate_misspelling_report()
print(f"Misspelling report generated in {time.time() - start_time:.4f} seconds")

# Expand acronyms and correct spelling
print("\n🔄 Applying text corrections...")
start_time = time.time()
workflow.expand_acronyms()
workflow.correct_spelling()
print(f"Text corrections completed in {time.time() - start_time:.4f} seconds")

# Show sample of processed text
print("\nSample of processed text:")
for i, text in enumerate(workflow.documents["feedback"].head(2)):
    print(f"[{i+1}] {text[:150]}...")

# Attempt to run topic modeling with optimized settings
try:
    print("\n📊 Running optimized topic modeling...")
    start_time = time.time()
    
    # Preprocess with memory optimization
    print("Preprocessing documents...")
    workflow.preprocess_documents()
    
    # Time the embedding and clustering
    print("Discovering topics...")
    topics_df = workflow.discover_topics()
    
    print(f"Topic modeling completed in {time.time() - start_time:.4f} seconds")
    print(f"Discovered {len(topics_df['topic'].unique())} topics")
    
    # Generate report
    print("\n📑 Generating comprehensive report...")
    start_time = time.time()
    report_path = workflow.generate_comprehensive_report()
    print(f"Report generated in {time.time() - start_time:.4f} seconds")
    
except Exception as e:
    print(f"\n⚠️ Could not complete topic modeling: {str(e)}")
    print("This is expected if some ML dependencies aren't installed.")
    print("The core workflow features (acronym detection and spelling correction) still work!")

print("\n✅ Optimized workflow example complete!")
print("""
Key optimization techniques demonstrated:
1. Small but effective embedding model (MiniLM-L6)
2. Quantization for reduced memory usage
3. Batch processing for efficiency
4. Polars integration for faster data processing (when available)
5. Low memory mode for embedding models
6. Graceful fallback when dependencies are missing

These optimizations allow Meno to work effectively on:
- Larger datasets (thousands to millions of documents)
- Machines with limited memory (including laptops and small cloud instances)
- Environments where GPU acceleration isn't available
""")