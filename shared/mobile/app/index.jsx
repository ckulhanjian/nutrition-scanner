import React, { useState, useEffect } from 'react';
import { View, Button, Image, StyleSheet, Alert, Text, Pressable, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { API } from "../config";


const Home = () => {
  const [image, setImage] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [uploadingIngredients, setUploadingIngredients] = useState(false); 

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
      alert("UPLOADING!")
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
        headers: {
          "Content-Type": "multipart/form-data",
        },
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


      {image ? (<Text style={styles.uploaded}>{image} uploaded</Text>) : (<Text style={styles.uploaded}>No image uploaded</Text>)}
      
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

      <Button>Analyze</Button>


      
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
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  title2 : {
    marginTop: 10,
    marginBottom: 10,
    fontSize: 18,
    fontWeight: '500',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 10,
    textAlign: 'center',
    marginBottom: 40,
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
  }
})