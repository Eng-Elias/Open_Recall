const FilterPanel = ({ filters, onFilterChange, appNameSuggestions }) => {
  const [showAppNameSuggestions, setShowAppNameSuggestions] =
    React.useState(false);
  const appNameRef = React.useRef(null);

  const handleInputChange = (field, value) => {
    onFilterChange({
      ...filters,
      [field]: value,
    });
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
    handleInputChange(field, localDate.toLocaleString());
  };

  const handleAppNameClick = (appName) => {
    handleInputChange("appName", appName);
    setShowAppNameSuggestions(false);
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
              onChange={(e) => {
                handleInputChange("appName", e.target.value);
                setShowAppNameSuggestions(true);
              }}
              placeholder="Filter by app..."
            />
            {showAppNameSuggestions && appNameSuggestions?.length > 0 && (
              <div className="app-name-suggestions">
                {appNameSuggestions
                  .filter((app) =>
                    app.toLowerCase().includes(filters.appName.toLowerCase())
                  )
                  .map((app) => (
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
      </div>
    </div>
  );
};
