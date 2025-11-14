import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image } from 'react-native';
import { useLocalSearchParams, useRouter } from "expo-router";

const Results = () => {
  const router = useRouter();
  const params = useLocalSearchParams();

  // If you passed data via query params
  const results = params.results ? JSON.parse(params.results) : null;
  const failing = params.failing ? JSON.parse(params.failing) : [];
  const filters = params.filters ? JSON.parse(params.filters) : [];

  // 
  const passedFilters = [];
  const failedFilters = [];

  filters.forEach((filter) => {
    const status = results[filter.name]; // e.g., "pass" or "fail"
    if (status === "pass") {
      passedFilters.push(filter);
    } else {
      failedFilters.push({
        ...filter,
        failedIngredients: failing[filter.name] || []
      });
    }
  });


  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Analysis Results</Text>

      {/* Failing Filters */}
      {failedFilters.length > 0 && (
        <View>
          <Text style={styles.groupTitle}>Failed Filters</Text>
          {failedFilters.map((filter) => (
            <View key={filter.id} style={[styles.filterOption, styles.filterFail]}>
              <Image source={filter.image} style={styles.filterImage} />
              <View style={{ flex: 1 }}>
                <Text style={styles.filterText}>{filter.displayName}</Text>
                {filter.failedIngredients.length > 0 && (
                  <Text style={styles.failedIngredients}>
                    {filter.failedIngredients.join(", ")}
                  </Text>
                )}
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Passed Filters */}
      {passedFilters.length > 0 && (
        <View>
          <Text style={styles.groupTitle}>Passed Filters</Text>
          {passedFilters.map((filter) => (
            <View key={filter.id} style={[styles.filterOption, styles.filterPass]}>
              <Image source={filter.image} style={styles.filterImage} />
              <Text style={styles.filterText}>{filter.displayName}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Scan Another Button */}
      <TouchableOpacity
        style={styles.scanButton}
        onPress={() => router.push("/")}
      >
        <Text style={styles.scanButtonText}>Scan Another Product</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

export default Results;

const styles = StyleSheet.create({
  container : {
    textAlign: 'center',
    padding: 20,
  },
  title : {
    fontSize: 32,
    textAlign: 'center',
    margin: 20,
    fontWeight: '700',
  },
  groupTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginVertical: 10,
  },
  filterOption: {
    flexDirection: "row",
    alignItems: "center",
    padding: 8,
    marginVertical: 4,
    borderWidth: 2,
    borderColor: "#aaa",
    borderRadius: 25,
  },
  filterFail: {
    backgroundColor: "#ffe5e5",
    borderColor: "#ff3b3b",
  },
  filterPass: {
    backgroundColor: "#edf8eb",
    borderColor: "#287912",
  },
  filterImage: {
    width: 40,
    height: 40,
    marginRight: 8,
  },
  filterText: {
    fontSize: 16,
    fontWeight: "600",
  },
  failedIngredients: {
    color: "#aa0000",
    fontSize: 14,
    marginTop: 2,
  },
  scanButton : {
    marginTop: 30,
    backgroundColor: "#4A90E2",
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 25,          // round pill shape
    minWidth: 120,
    alignItems: "center",
    justifyContent: "center",
  },
  scanButtonText : {
    color: "white",
    fontSize: 15,
    fontWeight: "600",
  }
});