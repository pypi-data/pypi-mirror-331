import os
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights

# Step 1: Load image paths and reference IDs from a JSON file
def load_image_paths_from_json(json_file):
    """
    Load image paths and reference IDs from a JSON file.
    The JSON file must contain 'Path' and 'Id' columns.
    """
    try:
        # Load the JSON file using pandas
        df = pd.read_json(json_file)
        
        # Ensure the JSON has the required columns: 'Path' and 'Id'
        if 'Path' not in df.columns or 'Id' not in df.columns:
            raise ValueError("JSON file must contain 'Path' and 'Id' columns.")
        
        # Extract image paths and reference IDs
        image_paths = df['Path'].tolist()
        reference_ids = df['Id'].tolist()
        
        return reference_ids, image_paths
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return [], []

# Step 2: Extract features from an image using a pre-trained model
def extract_features(img_path, model, transform):
    """
    Extract features from an image using a pre-trained ResNet50 model.
    """
    try:
        # Open and convert the image to RGB
        img = Image.open(img_path).convert('RGB')
        
        # Apply transformations and add batch dimension
        img_tensor = transform(img).unsqueeze(0)
        
        # Forward pass through the model (disable gradient computation)
        with torch.no_grad():
            features = model(img_tensor)
        
        # Convert to NumPy array and flatten
        return features.numpy().flatten()
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

# Step 3: Compare the given image with the bulk of images
def find_similar_image(query_image_path, bulk_image_paths, reference_ids, model, transform):
    """
    Compare the query image with a bulk of images and return the reference ID of the most similar image.
    """
    # Extract features for the query image
    query_features = extract_features(query_image_path, model, transform)
    if query_features is None:
        print("Failed to extract features for the query image.")
        return None

    # Extract features for all images in the bulk
    bulk_features = []
    valid_reference_ids = []  # To track corresponding reference IDs
    for img_path, ref_id in zip(bulk_image_paths, reference_ids):
        features = extract_features(img_path, model, transform)
        if features is not None:
            bulk_features.append(features)
            valid_reference_ids.append(ref_id)

    # Check if any valid features were extracted
    if len(bulk_features) == 0:
        print("No valid features extracted from bulk images.")
        return None

    # Compute cosine similarity between the query image and bulk images
    similarities = cosine_similarity([query_features], bulk_features).flatten()
    most_similar_index = np.argmax(similarities)  # Index of the most similar image

    # Return the reference ID of the most similar image
    return valid_reference_ids[most_similar_index]

# Step 4: Initialize the ResNet50 model and transformations
def initialize_model_and_transforms():
    """
    Initialize the pre-trained ResNet50 model and define image transformations.
    """
    # Load pre-trained ResNet50 weights
    weights = ResNet50_Weights.IMAGENET1K_V1
    model = resnet50(weights=weights)
    
    # Remove the final classification layer
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model.eval()  # Set the model to evaluation mode

    # Define image transformations
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to match model input size
        transforms.ToTensor(),          # Convert to tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize for ResNet
    ])

    return model, transform

# Main function
def find_reference_id(json_file, query_image_path):
    """
    Find the reference ID of the most similar image to the query image.
    Inputs:
        - json_file: Path to the JSON file containing image paths and IDs.
        - query_image_path: Path to the query image.
    Returns:
        - Reference ID of the most similar image, or an error message if no match is found.
    """
    # Load image paths and reference IDs from the JSON file
    reference_ids, bulk_image_paths = load_image_paths_from_json(json_file)
    if not reference_ids or not bulk_image_paths:
        return {"error": "Failed to load dataset."}

    # Initialize the model and transformations
    model, transform = initialize_model_and_transforms()

    # Find the reference ID of the most similar image
    reference_id = find_similar_image(
        query_image_path, bulk_image_paths, reference_ids, model, transform
    )

    if reference_id:
        return {reference_id}
    else:
        return {"No similar image found."}