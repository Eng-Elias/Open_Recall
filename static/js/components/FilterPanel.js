const FilterPanel = ({ filters, onFilterChange, appNameSuggestions }) => {
  const [showAppNameSuggestions, setShowAppNameSuggestions] =
    React.useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = React.useState([]);
  const appNameRef = React.useRef(null);
  const [showSummaryModal, setShowSummaryModal] = React.useState(false);
  const [summary, setSummary] = React.useState("");
  const [isSummarizing, setIsSummarizing] = React.useState(false);
  const [summaryError, setSummaryError] = React.useState(null);
  const [settings, setSettings] = React.useState({
    enable_summarization: false,
  });

  const handleInputChange = (field, value) => {
    onFilterChange(field, value);
  };

  const formatDateTimeForInput = (isoString) => {
    if (!isoString) return "";
    // Convert UTC ISO string to local datetime-local input value
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const handleDateTimeChange = (field, value) => {
    if (!value) {
      handleInputChange(field, null);
      return;
    }
    // Convert local datetime to UTC ISO string
    const localDate = new Date(value);
    handleInputChange(field, localDate.toISOString());
  };

  const handleAppNameChange = (value) => {
    handleInputChange("appName", value);
    setShowAppNameSuggestions(true);

    // Filter suggestions based on input
    if (value.trim() === "") {
      setFilteredSuggestions([]);
    } else {
      const filtered = appNameSuggestions.filter((app) =>
        app.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredSuggestions(filtered);
    }
  };

  const handleAppNameClick = (appName) => {
    handleInputChange("appName", appName);
    setShowAppNameSuggestions(false);
    setFilteredSuggestions([]);
  };

  const handleSummarizeClick = async () => {
    setIsSummarizing(true);
    setSummaryError(null);
    setSummary("");
    setShowSummaryModal(true);

    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);
      if (filters.appName) params.append("app_name", filters.appName);
      if (filters.isFavorite !== undefined)
        params.append("is_favorite", filters.isFavorite);
      if (filters.tagIds && filters.tagIds.length > 0) {
        filters.tagIds.forEach((tagId) => {
          params.append("tag_ids", tagId);
        });
      }
      if (filters.searchText) params.append("search_text", filters.searchText);

      const response = await fetch(
        `/api/summarize-search?${params.toString()}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSummary(data.summary);
      } else {
        const errorData = await response.json();
        setSummaryError(errorData.detail || "Failed to generate summary");
      }
    } catch (error) {
      console.error("Error summarizing screenshots:", error);
      setSummaryError("An error occurred while summarizing screenshots");
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleCloseSummaryModal = () => {
    setShowSummaryModal(false);
  };

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (appNameRef.current && !appNameRef.current.contains(event.target)) {
        setShowAppNameSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/settings");
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (error) {
      console.error("Error fetching settings:", error);
    }
  };

  // Fetch settings when component mounts
  React.useEffect(() => {
    fetchSettings();
  }, []);

  // Format filter values for display in the summary modal
  const getFilterSummary = () => {
    const parts = [];

    if (filters.startDate) {
      const startDate = new Date(filters.startDate);
      parts.push(`From: ${startDate.toLocaleString()}`);
    }

    if (filters.endDate) {
      const endDate = new Date(filters.endDate);
      parts.push(`To: ${endDate.toLocaleString()}`);
    }

    if (filters.appName) {
      parts.push(`App: ${filters.appName}`);
    }

    if (filters.searchText) {
      parts.push(`Text: "${filters.searchText}"`);
    }

    if (filters.isFavorite) {
      parts.push("Favorites only");
    }

    return parts.join(" • ");
  };

  return (
    <div className="filter-panel">
      <div className="row g-3">
        <div className="col-md-3">
          <label className="form-label">Start Date & Time</label>
          <input
            type="datetime-local"
            className="form-control"
            value={formatDateTimeForInput(filters.startDate)}
            onChange={(e) => handleDateTimeChange("startDate", e.target.value)}
          />
        </div>
        <div className="col-md-3">
          <label className="form-label">End Date & Time</label>
          <input
            type="datetime-local"
            className="form-control"
            value={formatDateTimeForInput(filters.endDate)}
            onChange={(e) => handleDateTimeChange("endDate", e.target.value)}
          />
        </div>
        <div className="col-md-3" ref={appNameRef}>
          <label className="form-label">App Name</label>
          <div className="app-name-autocomplete">
            <input
              type="text"
              className="form-control"
              value={filters.appName}
              onChange={(e) => handleAppNameChange(e.target.value)}
              placeholder="Filter by app..."
            />
            {showAppNameSuggestions && filteredSuggestions.length > 0 && (
              <div className="app-name-suggestions">
                {filteredSuggestions.map((app) => (
                  <div
                    key={app}
                    className="app-name-suggestion"
                    onClick={() => handleAppNameClick(app)}
                  >
                    {app}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="col-md-3">
          <label className="form-label">Search Text</label>
          <input
            type="text"
            className="form-control"
            value={filters.searchText}
            onChange={(e) => handleInputChange("searchText", e.target.value)}
            placeholder="Search in text..."
          />
        </div>
        <div className="col-md-3">
          <div className="form-check mt-4">
            <input
              type="checkbox"
              className="form-check-input"
              checked={filters.isFavorite}
              onChange={(e) =>
                handleInputChange("isFavorite", e.target.checked)
              }
              id="favoriteFilter"
            />
            <label className="form-check-label" htmlFor="favoriteFilter">
              Show Favorites Only
            </label>
          </div>
        </div>
        {/* Only show the summarize button if summarization is enabled */}
        {settings.enable_summarization && (
          <div className="col-md-3">
            <div className="mt-4">
              <button
                className="btn btn-outline-primary"
                onClick={handleSummarizeClick}
                type="button"
              >
                <i className="bi bi-file-text me-2"></i>
                Summarize Results
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Summary Modal */}
      {showSummaryModal && (
        <div
          className="modal"
          tabIndex="-1"
          role="dialog"
          style={{ display: "block", backgroundColor: "rgba(0,0,0,0.5)" }}
        >
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Search Results Summary</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={handleCloseSummaryModal}
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body overflow-auto">
                <div className="mb-3">
                  <strong>Filters: </strong>
                  <span className="text-muted">
                    {getFilterSummary() || "None"}
                  </span>
                </div>

                {isSummarizing ? (
                  <div className="text-center p-4">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3">
                      Generating summary... This may take a moment.
                    </p>
                  </div>
                ) : summaryError ? (
                  <div className="alert alert-danger">{summaryError}</div>
                ) : (
                  <div className="p-3 border rounded bg-light">
                    {summary ? (
                      <p className="mb-0">{summary}</p>
                    ) : (
                      <p className="text-muted mb-0">No summary available.</p>
                    )}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCloseSummaryModal}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
