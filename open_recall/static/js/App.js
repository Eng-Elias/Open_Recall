const App = () => {
  const [screenshots, setScreenshots] = React.useState({
    items: [],
    page: 1,
    pages: 1,
  });
  const [filters, setFilters] = React.useState({
    startDate: "",
    endDate: "",
    appName: "",
    isFavorite: false,
    tagIds: [],
    searchText: "",
  });
  const [allTags, setAllTags] = React.useState([]);
  const [currentPage, setCurrentPage] = React.useState(1);
  const [appNameSuggestions, setAppNameSuggestions] = React.useState([]);
  const [ws, setWs] = React.useState(null);
  const [selectedScreenshot, setSelectedScreenshot] = React.useState(null);

  // Check if a screenshot matches current filters
  const matchesFilters = (screenshot) => {
    // App name filter
    if (
      filters.appName &&
      !screenshot.app_name
        ?.toLowerCase()
        .includes(filters.appName.toLowerCase())
    ) {
      return false;
    }

    // Favorite filter
    if (filters.isFavorite && !screenshot.is_favorite) {
      return false;
    }

    // Date range filter
    if (filters.startDate || filters.endDate) {
      const screenshotDate = new Date(screenshot.timestamp);
      if (filters.startDate) {
        const startDate = new Date(filters.startDate);
        if (screenshotDate < startDate) return false;
      }
      if (filters.endDate) {
        const endDate = new Date(filters.endDate);
        endDate.setHours(23, 59, 59, 999); // End of day
        if (screenshotDate > endDate) return false;
      }
    }

    // Tag filter
    if (filters.tagIds.length > 0) {
      const screenshotTagIds = screenshot.tags.map((tag) => tag.id);
      if (!filters.tagIds.every((tagId) => screenshotTagIds.includes(tagId))) {
        return false;
      }
    }

    // Search text filter
    if (filters.searchText) {
      const searchLower = filters.searchText.toLowerCase();
      const textMatch =
        screenshot.app_name?.toLowerCase().includes(searchLower) ||
        screenshot.window_title?.toLowerCase().includes(searchLower) ||
        screenshot.extracted_text?.toLowerCase().includes(searchLower);
      if (!textMatch) return false;
    }

    return true;
  };

  // WebSocket setup
  React.useEffect(() => {
    const websocket = new WebSocket(`ws://${window.location.host}/ws`);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "favorite_updated":
          setScreenshots((prev) => {
            const updatedItems = prev.items.map((screenshot) =>
              screenshot.id === data.screenshot_id
                ? { ...screenshot, is_favorite: data.is_favorite }
                : screenshot
            );
            return {
              ...prev,
              items: updatedItems.filter(matchesFilters),
            };
          });
          break;

        case "tag_added":
          setScreenshots((prev) => {
            const updatedItems = prev.items.map((screenshot) =>
              screenshot.id === data.screenshot_id
                ? {
                    ...screenshot,
                    tags: [...screenshot.tags, data.tag],
                  }
                : screenshot
            );
            return {
              ...prev,
              items: updatedItems.filter(matchesFilters),
            };
          });
          break;

        case "tag_removed":
          setScreenshots((prev) => {
            const updatedItems = prev.items.map((screenshot) =>
              screenshot.id === data.screenshot_id
                ? {
                    ...screenshot,
                    tags: screenshot.tags.filter(
                      (tag) => tag.id !== data.tag_id
                    ),
                  }
                : screenshot
            );
            return {
              ...prev,
              items: updatedItems.filter(matchesFilters),
            };
          });
          break;

        case "new_screenshot":
          if (matchesFilters(data.screenshot)) {
            setScreenshots((prev) => ({
              ...prev,
              items: [data.screenshot, ...prev.items].slice(
                0,
                prev.items.length
              ),
              total: prev.total + 1,
              pages: Math.ceil((prev.total + 1) / 12),
            }));
          }
          break;

        case "settings_updated":
          // Handle settings update if needed
          console.log("Settings updated:", data.settings);
          break;
      }
    };

    setWs(websocket);
    return () => websocket.close();
  }, [filters]); // Re-establish connection when filters change

  const fetchScreenshots = async (page = currentPage) => {
    const params = new URLSearchParams({
      page: page,
      size: 12,
      ...(filters.startDate && { start_date: filters.startDate }),
      ...(filters.endDate && { end_date: filters.endDate }),
      ...(filters.appName && { app_name: filters.appName }),
      ...(filters.isFavorite && { is_favorite: filters.isFavorite }),
      ...(filters.searchText && { search_text: filters.searchText }),
    });

    if (filters.tagIds.length > 0) {
      filters.tagIds.forEach((id) => params.append("tag_ids", id));
    }

    const response = await fetch(`/api/screenshots?${params}`);
    const data = await response.json();
    setScreenshots(data);
  };

  const fetchTags = async () => {
    const response = await fetch("/api/tags");
    const data = await response.json();
    setAllTags(data);
  };

  const fetchAppNames = async () => {
    const response = await fetch("/api/app-names");
    const data = await response.json();
    setAppNameSuggestions(data);
  };

  React.useEffect(() => {
    fetchScreenshots();
    fetchTags();
    fetchAppNames();
  }, []);

  React.useEffect(() => {
    fetchScreenshots();
  }, [filters, currentPage]);

  // Initialize tooltips when selected screenshot changes
  React.useEffect(() => {
    if (selectedScreenshot) {
      // Initialize tooltips
      const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
      );
      tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }
  }, [selectedScreenshot]);

  const handleFilterChange = (name, value) => {
    setFilters((prev) => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleToggleFavorite = async (screenshotId) => {
    try {
      const response = await fetch(`/api/toggle-favorite/${screenshotId}`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to toggle favorite");
      }
      await fetchScreenshots(currentPage);
    } catch (error) {
      console.error("Error toggling favorite:", error);
    }
  };

  const handleAddTag = async (screenshotId, tagId) => {
    try {
      const response = await fetch(`/api/add-tag/${screenshotId}/${tagId}`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to add tag");
      }
      await fetchScreenshots(currentPage);
    } catch (error) {
      console.error("Error adding tag:", error);
    }
  };

  const handleRemoveTag = async (screenshotId, tagId) => {
    try {
      const response = await fetch(`/api/remove-tag/${screenshotId}/${tagId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to remove tag");
      }
      await fetchScreenshots(currentPage);
    } catch (error) {
      console.error("Error removing tag:", error);
    }
  };

  const handleDeleteTag = async (tagId) => {
    try {
      // First check if the tag is selected in filters
      if (filters.tagIds.includes(tagId)) {
        // Remove it from filters first
        const newTagIds = filters.tagIds.filter((id) => id !== tagId);
        handleFilterChange("tagIds", newTagIds);
      }

      const response = await fetch(`/api/tags/${tagId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to delete tag");
      }

      // Refresh the tags list
      await fetchTags();
    } catch (error) {
      console.error("Error deleting tag:", error);
    }
  };

  const handleScreenshotsDeleted = async (count) => {
    // Refresh the screenshots list after deletion
    await fetchScreenshots(1); // Reset to first page
    setCurrentPage(1);
  };

  return (
    <div className="container-fluid">
      <div className="mb-4">
        <div className="text-center py-2">
          <img
            src="/static/images/logo.png"
            alt="Open_Recall Logo"
            height="70"
            className="ms-2"
          />
        </div>
        <SettingsPanel />
        <DeleteScreenshotsPanel
          onScreenshotsDeleted={handleScreenshotsDeleted}
        />
        <TagManager
          allTags={allTags}
          onTagsUpdate={fetchTags}
          selectedTagIds={filters.tagIds}
          onTagSelect={(tagId) => {
            const newTagIds = filters.tagIds.includes(tagId)
              ? filters.tagIds.filter((id) => id !== tagId)
              : [...filters.tagIds, tagId];
            handleFilterChange("tagIds", newTagIds);
          }}
          onDeleteTag={handleDeleteTag}
        />
        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          appNameSuggestions={appNameSuggestions}
        />
      </div>
      <div className="row">
        <div className="col-12">
          <ScreenshotGrid
            screenshots={screenshots}
            allTags={allTags}
            onToggleFavorite={handleToggleFavorite}
            onAddTag={handleAddTag}
            onRemoveTag={handleRemoveTag}
            currentPage={currentPage}
            onPageChange={handlePageChange}
            refetch={() => fetchScreenshots(currentPage)}
            onSelectScreenshot={(screenshot) =>
              setSelectedScreenshot(screenshot)
            }
          />
        </div>
      </div>
    </div>
  );
};

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<App />);
