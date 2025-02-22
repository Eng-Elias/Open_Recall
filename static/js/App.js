const App = () => {
  const [screenshots, setScreenshots] = React.useState(null);
  const [allTags, setAllTags] = React.useState([]);
  const [appNames, setAppNames] = React.useState([]);
  const [filters, setFilters] = React.useState({
    startDate: "",
    endDate: "",
    appName: "",
    isFavorite: false,
    selectedTags: [],
    searchText: "",
    page: 1,
  });
  const [loading, setLoading] = React.useState(true);

  // Fetch screenshots with current filters
  const fetchScreenshots = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      // Only add date parameters if they have values
      if (filters.startDate) {
        params.append("start_date", filters.startDate);
      }
      if (filters.endDate) {
        params.append("end_date", filters.endDate);
      }
      
      if (filters.appName) {
        params.append("app_name", filters.appName);
      }
      if (filters.isFavorite) {
        params.append("is_favorite", true);
      }
      if (filters.selectedTags.length > 0) {
        filters.selectedTags.forEach((tagId) => {
          params.append("tag_ids", tagId);
        });
      }
      if (filters.searchText) {
        params.append("search_text", filters.searchText);
      }
      params.append("page", filters.page);

      const response = await fetch(`/api/screenshots?${params.toString()}`);
      const data = await response.json();
      setScreenshots(data);
    } catch (error) {
      console.error("Error fetching screenshots:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await fetch("/api/tags");
      const data = await response.json();
      setAllTags(data);
    } catch (error) {
      console.error("Error fetching tags:", error);
    }
  };

  const fetchAppNames = async () => {
    try {
      const response = await fetch("/api/app-names");
      const data = await response.json();
      setAppNames(data);
    } catch (error) {
      console.error("Error fetching app names:", error);
    }
  };

  React.useEffect(() => {
    fetchTags();
    fetchAppNames();
  }, []);

  React.useEffect(() => {
    fetchScreenshots();
  }, [filters]);

  const handleFilterChange = (newFilters) => {
    setFilters({ ...newFilters, page: 1 }); // Reset to page 1 when filters change
  };

  const handlePageChange = (newPage) => {
    setFilters({ ...filters, page: newPage });
  };

  const handleTagSelect = (tagId) => {
    const selectedTags = filters.selectedTags.includes(tagId)
      ? filters.selectedTags.filter((id) => id !== tagId)
      : [...filters.selectedTags, tagId];
    setFilters({ ...filters, selectedTags, page: 1 }); // Reset to page 1 when tags change
  };

  const handleTagCreate = async (tagName) => {
    try {
      const response = await fetch("/api/tags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: tagName }),
      });
      if (response.ok) {
        fetchTags();
      }
    } catch (error) {
      console.error("Error creating tag:", error);
    }
  };

  const handleToggleFavorite = async (screenshotId) => {
    try {
      const response = await fetch(
        `/api/screenshots/${screenshotId}/favorite`,
        {
          method: "PUT",
        }
      );
      if (response.ok) {
        fetchScreenshots();
      }
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  };

  // Add tag to screenshot
  const handleAddTag = async (screenshotId, tagId) => {
    try {
      const response = await fetch(
        `/api/screenshots/${screenshotId}/tags/${tagId}`,
        {
          method: "POST",
        }
      );
      if (response.ok) {
        fetchScreenshots();
      }
    } catch (error) {
      console.error("Error adding tag:", error);
    }
  };

  // Remove tag from screenshot
  const handleRemoveTag = async (screenshotId, tagId) => {
    try {
      const response = await fetch(
        `/api/screenshots/${screenshotId}/tags/${tagId}`,
        {
          method: "DELETE",
        }
      );
      if (response.ok) {
        fetchScreenshots();
      }
    } catch (error) {
      console.error("Error removing tag:", error);
    }
  };

  return (
    <div className="container-fluid py-4">
      <h1 className="mb-4">OpenRecall Screenshots</h1>

      <FilterPanel 
        filters={filters} 
        onFilterChange={handleFilterChange} 
        appNameSuggestions={appNames}
      />

      <TagManager
        selectedTags={filters.selectedTags}
        allTags={allTags}
        onTagSelect={handleTagSelect}
        onTagCreate={handleTagCreate}
      />

      <div className="screenshots-container">
        {loading ? (
          <div className="loading-spinner">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : (
          <ScreenshotGrid
            screenshots={screenshots}
            allTags={allTags}
            onToggleFavorite={handleToggleFavorite}
            onAddTag={handleAddTag}
            onRemoveTag={handleRemoveTag}
            currentPage={filters.page}
            onPageChange={handlePageChange}
          />
        )}
      </div>
    </div>
  );
};

// Render the App
ReactDOM.render(<App />, document.getElementById("root"));
