import React, { useState, useEffect } from 'react';
import { View, Button, Image, StyleSheet, Alert, Text, Pressable, TouchableOpacity, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { API } from "../config";
import { useRouter } from 'expo-router';


const Home = () => {
  const router = useRouter();
  const [image, setImage] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [uploadingIngredients, setUploadingIngredients] = useState(false); 
  const [isAnalyzing, setIsAnalyzing] = useState(false); 
  const [fullAnalysis, setFullAnalysis] = useState(false);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState(null);
  const [failing, setFailing] = useState(null);
  const [filters, setFilters] = useState([
    { id: "lactose", name: "lactose-intolerant", displayName: "Lactose Intolerant", image: require("../icons/lactose.png"), checked: false },
    { id: "vegan", name: "vegan", displayName: "Vegan", image: require("../icons/vegan.png"), checked: false },
    { id: "vegetarian", name: "vegetarian", displayName: "Vegetarian", image: require("../icons/vegetarian.png"), checked: false },
    { id: "halal", name: "halal", displayName: "Halal", image: require("../icons/halal.png"), checked: false },
    { id: "lowsugar", name: "low-sugar", displayName: "Low-Sugar", image: require("../icons/low-sugar.png"), checked: false },
    { id: "glutenfree", name: "gluten-free", displayName: "Gluten-Free", image: require("../icons/gluten-free.png"), checked: false }
  ]);

  // will also need to check for filters
  useEffect(() => {
    if (image && !uploadingIngredients && ingredients.length === 0) {
      // alert("UPLOADING!")
      handleUploadSubmit();
    }
  }, [image]);

  const takePhoto = async () => {
    // grant permission
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      alert("Camera permission required!");
      return;
    }
    // launch camera
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });
    // make sure it goes through
    if (!result.canceled) {
      setImage(result.assets[0].uri);
      console.log("image set");
    }
  };

  const uploadPhoto = async () => {
    // permission
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      alert("Permission required!");
      return;
    }
    // launch image picker
    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      console.log("image set");
    }
  };

  const handleUploadSubmit = async () => {
    if (!image) return;
    
    // get file extension
    const uriParts = image.split('.');
    // extension is the last item in list
    const fileType = uriParts[uriParts.length - 1].toLowerCase();
    
    // map file extension to types
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'heic': 'image/heic',
      'heif': 'image/heif',
    };
    // default jpeg
    const mimeType = mimeTypes[fileType] || 'image/jpeg';
    
    const formData = new FormData();
    formData.append("file", {
      uri: image,
      name: `photo.${fileType}`, // how do we get name - photo ?
      type: mimeType,
    });
    
    setUploadingIngredients(true); // start getting ingredients
    try {
      // alert(`Uploading to: ${API.upload}`); // Show what URL we're using (TESTING)
      
      const uploadResponse = await fetch(API.upload, {
        method: "POST",
        body: formData,
        // headers: {
        //   "Content-Type": "multipart/form-data",
        // },
      });

      if (!uploadResponse.ok) {
        throw new Error(`HTTP error! status: ${uploadResponse.status}`);
      }

      const { job_id, ingredients } = await uploadResponse.json();
      // alert(`Success! Found ${ingredients.length} ingredients`);
      setIngredients(ingredients);
      setJobId(job_id);
    } catch (error) {
      alert(`Error: ${error.message}\n\nMake sure:\n1. Backend is running\n2. Phone and computer on same WiFi\n3. API.upload has your computer's IP`);
    } finally {
      setUploadingIngredients(false);
    }
  };

  // filters
  const handleFilterToggle = (id) => {
    setFilters(prev =>
      prev.map(filter =>
        filter.id === id ? { ...filter, checked: !filter.checked } : filter
      )
    );
  };

  const analyzeIngredients = async () => {
    // Check if ingredients exist
    // if (!ingredients || ingredients.length === 0) {
    //   alert("No image uploaded.");
    //   return;
    // }
    setFullAnalysis(true);

    // Check if at least one filter is selected
    const selectedFilters = filters
      .filter(f => f.checked)
      .map(f => f.name);
    if (selectedFilters.length === 0) {
      alert("Please select at least one filter");
      return;
    }

    // Check if an image was uploaded
    if (!image) {
      alert("Please upload a photo.");
      return;
    }

    let attempts = 0;
      while ((!ingredients || ingredients.length === 0) && attempts < 20) {
        await new Promise(res => setTimeout(res, 500)); // wait 0.5s
        attempts++;
      }

      if (!ingredients || ingredients.length === 0) {
        alert("Ingredients not ready yet. Please try again.");
        setFullAnalysis(false);
        return;
      }

    try {
      // Send analysis request
      const response = await fetch(API.analyze, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          ingredients,
          filters: selectedFilters,
          image_uri: image, // assuming your image object has a 'uri'
        }),
      });

      const data = await response.json();
      setStatus("pending");

      // Polling for results every 2 seconds
      const interval = setInterval(async () => {
        try {
          const statusResponse = await fetch(API.status(jobId));
          const statusData = await statusResponse.json();

          if (statusData.status === "complete") {
            setStatus("complete");

            // Fetch final results
            const resultsResponse = await fetch(API.results(jobId));
            const resultsData = await resultsResponse.json();

            setResults(resultsData.results);
            setFailing(resultsData.failing);

            clearInterval(interval);
            // setIsAnalyzing(false);
            router.push({
              pathname: "/results",
              params: {
                results: JSON.stringify(resultsData.results),
                failing: JSON.stringify(resultsData.failing),
                filters: JSON.stringify(filters.filter(f => f.checked))
              },
            });
          }
        } catch (err) {
          console.error("Polling error:", err);
          setStatus("error");
          clearInterval(interval);
          setFullAnalysis(false);
        }
      }, 2000);
    } catch (err) {
      console.error("Analyze request failed:", err);
      alert("Failed to analyze ingredients. Please try again.");
      setFullAnalysis(false);
    }
  };

  return (
    <View style={styles.container}>
      {!fullAnalysis ? (
        <View style={styles.container}>
      <Text style={styles.title}>Nouri</Text>
      {/* <Text style={styles.subtitle}>
        Let's sift through all those ingredients to keep you healthy and safe!
      </Text> */}

      <Text style={styles.title2}>1. Upload Image</Text>
      <View style={styles.photoButtons}>
        <TouchableOpacity style={[styles.primaryButton, isAnalyzing && styles.disabledButton]} onPress={takePhoto} disabled={isAnalyzing}>
          <Text style={styles.buttonText} >Take Photo</Text>
        </TouchableOpacity>

        <Text style={styles.orText}>or</Text>

        <TouchableOpacity style={[styles.primaryButton, isAnalyzing && styles.disabledButton]} disabled={isAnalyzing} onPress={uploadPhoto}>
          <Text style={styles.buttonText}>Upload Photo</Text>
        </TouchableOpacity>
      </View>


      {image ? (<Text style={styles.uploaded}>Image uploaded ✅</Text>) : (<Text style={styles.uploaded}>No image uploaded</Text>)}
      
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
          (!image || !filters.some(f => f.checked)) && styles.disabledButton
        ]}
        onPress={analyzeIngredients}
        disabled={!image || !filters.some(f => f.checked)}
      >
        <Text style={styles.analyzeButtonText}>Analyze
        </Text>
      </TouchableOpacity>
    </View>
    ) : (
      <View>
        <ActivityIndicator size="large" color="#000000ff" />
        <Text style={styles.waitingText}>Please wait while ingredients are analyzed.</Text>
      </View>
    )}
    </View>
  )
}

export default Home

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  photoButtons: {
    flexDirection: "row",
    alignItems: "center",      // vertical center
    justifyContent: "center",  // horizontal center
    gap: 12,                   // spacing between elements (RN 0.71+)
  },

  primaryButton: {
    backgroundColor: "#4A90E2",
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 25,          // round pill shape
    minWidth: 120,
    alignItems: "center",
    justifyContent: "center",
  },
  waitingText : {
    margin: 30,
    fontSize: 24,
    selfAlign: 'center',
    textAlign: 'center',
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
  uploaded : {
    color: 'gray',
    textAlign: 'center',
    margin: 15,
    fontWeight: 400,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  title2 : {
    marginTop: 20,
    marginBottom: 10,
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 10,
    marginBottom: 40,
    width: '80%',
    textAlign: 'center',
    alignSelf: 'center',
  },
  image: {
    width: 300,
    height: 300,
    marginVertical: 20,
    alignSelf: 'center',
  },
  ingredientsContainer: {
    marginTop: 20,
  },
  ingredientsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  ingredient: {
    fontSize: 14,
    marginBottom: 5,
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
    width: '90%',
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
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: "#555",
    borderRadius: 4,
  },
  checkboxChecked: {
    backgroundColor: "#3ba6de",
    borderColor: "#3ba6de",
  },
  analyzeButton: {
    backgroundColor: "#4A90E2",
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 25,     // fully rounded
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
    backgroundColor: "#a0c4e8",   // lighter color when disabled
  },
})