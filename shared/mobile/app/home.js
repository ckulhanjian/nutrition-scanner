import React, { useState, useEffect } from 'react';
import { View, Button, Image, StyleSheet, Alert, Text, Pressable, TouchableOpacity, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { API } from "../config";


const Home = ({ navigation }) => {
  const [image, setImage] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [uploadingIngredients, setUploadingIngredients] = useState(false); 
  const [isAnalyzing, setIsAnalyzing] = useState(false); 

  const [filters, setFilters] = useState([
    { id: "lactose", name: "lactose-intolerant", displayName: "Lactose Intolerant", image: require("../icons/lactose.png"), checked: false },
    { id: "vegan", name: "vegan", displayName: "Vegan", image: require("../icons/vegan.png"), checked: false },
    { id: "vegetarian", name: "vegetarian", displayName: "Vegetarian", image: require("../icons/vegetarian.png"), checked: false },
    { id: "halal", name: "halal", displayName: "Halal", image: require("../icons/halal.png"), checked: false },
    { id: "lowsugar", name: "low-sugar", displayName: "Low-Sugar", image: require("../icons/low-sugar.png"), checked: false },
    { id: "glutenfree", name: "gluten-free", displayName: "Gluten-Free", image: require("../icons/gluten-free.png"), checked: false }
  ]);

  // Auto-upload when image is selected
  useEffect(() => {
    if (image && !uploadingIngredients && ingredients.length === 0) {
      handleUploadSubmit();
    }
  }, [image]);

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      alert("Camera permission required!");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });
    if (!result.canceled) {
      setImage(result.assets[0].uri);
      // Reset ingredients when new image is selected
      setIngredients([]);
      setJobId(null);
    }
  };

  const uploadPhoto = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      alert("Permission required!");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      // Reset ingredients when new image is selected
      setIngredients([]);
      setJobId(null);
    }
  };

  const handleUploadSubmit = async () => {
    if (!image) return;
    
    const uriParts = image.split('.');
    const fileType = uriParts[uriParts.length - 1].toLowerCase();
    
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'heic': 'image/heic',
      'heif': 'image/heif',
    };
    const mimeType = mimeTypes[fileType] || 'image/jpeg';
    
    const formData = new FormData();
    formData.append("file", {
      uri: image,
      name: `photo.${fileType}`,
      type: mimeType,
    });
    
    setUploadingIngredients(true);
    try {
      const uploadResponse = await fetch(API.upload, {
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (!uploadResponse.ok) {
        throw new Error(`HTTP error! status: ${uploadResponse.status}`);
      }

      const { job_id, ingredients } = await uploadResponse.json();
      setIngredients(ingredients);
      setJobId(job_id);
    } catch (error) {
      alert(`Error: ${error.message}\n\nMake sure:\n1. Backend is running\n2. Phone and computer on same WiFi\n3. API.upload has your computer's IP`);
      // Reset image on error so user can try again
      setImage(null);
    } finally {
      setUploadingIngredients(false);
    }
  };

  const handleFilterToggle = (id) => {
    setFilters(prev =>
      prev.map(filter =>
        filter.id === id ? { ...filter, checked: !filter.checked } : filter
      )
    );
  };

  const analyzeIngredients = async () => {
    // Validation
    if (!image) {
      alert("Please upload a photo before analyzing");
      return;
    }

    const selectedFilters = filters.filter(f => f.checked).map(f => f.name);
    if (selectedFilters.length === 0) {
      alert("Please select at least one filter");
      return;
    }

    // CRITICAL: Wait for ingredient extraction to complete
    if (uploadingIngredients) {
      alert("Please wait for ingredient extraction to complete...");
      return;
    }

    if (!ingredients || ingredients.length === 0) {
      alert("No ingredients detected. Please try uploading a different image.");
      return;
    }

    if (!jobId) {
      alert("Upload error. Please try again.");
      return;
    }

    setIsAnalyzing(true);

    try {
      // Send analysis request
      const response = await fetch(API.analyze, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          ingredients,
          filters: selectedFilters,
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
      }

      const data = await response.json();

      // Poll for results
      const pollResults = async () => {
        return new Promise((resolve, reject) => {
          const interval = setInterval(async () => {
            try {
              const statusResponse = await fetch(API.status(jobId));
              const statusData = await statusResponse.json();

              if (statusData.status === "complete") {
                clearInterval(interval);

                // Fetch final results
                const resultsResponse = await fetch(API.results(jobId));
                const resultsData = await resultsResponse.json();

                resolve(resultsData);
              } else if (statusData.status === "error") {
                clearInterval(interval);
                reject(new Error("Analysis failed on server"));
              }
            } catch (err) {
              clearInterval(interval);
              reject(err);
            }
          }, 2000);

          // Timeout after 60 seconds
          setTimeout(() => {
            clearInterval(interval);
            reject(new Error("Analysis timeout"));
          }, 60000);
        });
      };

      const resultsData = await pollResults();

      // Navigate to Results screen
      navigation.navigate('Results', {
        results: resultsData.results,
        failing: resultsData.failing,
        filters: filters,
      });

    } catch (err) {
      console.error("Analyze request failed:", err);
      alert("Failed to analyze ingredients. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sift</Text>
      <Text style={styles.subtitle}>
        Let's sift through all those ingredients to keep you healthy and safe!
      </Text>

      <Text style={styles.title2}>1. Upload Image</Text>
      <View style={styles.photoButtons}>
        <TouchableOpacity style={styles.primaryButton} onPress={takePhoto}>
          <Text style={styles.buttonText}>Take Photo</Text>
        </TouchableOpacity>

        <Text style={styles.orText}>or</Text>

        <TouchableOpacity style={styles.primaryButton} onPress={uploadPhoto}>
          <Text style={styles.buttonText}>Upload Photo</Text>
        </TouchableOpacity>
      </View>

      {/* Status Messages */}
      {uploadingIngredients ? (
        <View style={styles.statusContainer}>
          <ActivityIndicator size="small" color="#4A90E2" />
          <Text style={styles.statusText}>Extracting ingredients...</Text>
        </View>
      ) : image && ingredients.length > 0 ? (
        <Text style={styles.uploaded}>✅ Image uploaded • {ingredients.length} ingredients found</Text>
      ) : image ? (
        <Text style={styles.uploaded}>⚠️ No ingredients detected</Text>
      ) : (
        <Text style={styles.uploaded}>No image uploaded</Text>
      )}
      
      <Text style={styles.title2}>2. Select all filters</Text>
      <View style={styles.filtersContainer}>
        {filters.map((filter) => (
          <Pressable
            key={filter.id}
            onPress={() => handleFilterToggle(filter.id)}
            style={[
              styles.filterOption,
              filter.checked && styles.filterOptionChecked
            ]}
          >
            <Image source={filter.image} style={styles.filterImage} />
            <Text style={styles.filterText}>{filter.displayName}</Text>
          </Pressable>
        ))}
      </View>

      <TouchableOpacity
        style={[
          styles.analyzeButton,
          (uploadingIngredients || ingredients.length === 0 || !filters.some(f => f.checked)) && styles.disabledButton
        ]}
        onPress={analyzeIngredients}
        disabled={uploadingIngredients || ingredients.length === 0 || !filters.some(f => f.checked)}
      >
        <Text style={styles.analyzeButtonText}>
          {isAnalyzing ? "Analyzing..." : "Analyze"}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default Home;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  photoButtons: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  primaryButton: {
    backgroundColor: "#4A90E2",
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 25,
    minWidth: 120,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 15,
    fontWeight: "600",
  },
  orText: {
    fontSize: 14,
    color: "#555",
    fontWeight: "500",
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 15,
    gap: 8,
  },
  statusText: {
    color: '#4A90E2',
    fontSize: 14,
    fontWeight: '500',
  },
  uploaded: {
    color: 'gray',
    textAlign: 'center',
    margin: 15,
    fontWeight: '400',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  title2: {
    marginTop: 10,
    marginBottom: 10,
    fontSize: 18,
    fontWeight: '500',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 40,
    width: '80%',
    textAlign: 'center',
    alignSelf: 'center',
  },
  filtersContainer: {
    gap: 10,
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },
  filterOption: {
    flexDirection: "row",
    alignItems: "center",
    padding: 4,
    width: '48%',
    borderWidth: 2,
    borderColor: "#aaa",
    borderRadius: 25,
  },
  filterOptionChecked: {
    backgroundColor: "#edf8ebff",
    borderColor: "#287912ff",
  },
  filterImage: {
    width: 40,
    height: 40,
    marginRight: 8,
  },
  filterText: {
    fontSize: 18,
    flex: 1,
  },
  analyzeButton: {
    backgroundColor: "#4A90E2",
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 25,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 50,
  },
  analyzeButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  disabledButton: {
    backgroundColor: "#a0c4e8",
  },
});