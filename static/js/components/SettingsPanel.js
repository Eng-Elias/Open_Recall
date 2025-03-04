const SettingsPanel = () => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [settings, setSettings] = React.useState({
    enable_summarization: false,
    capture_interval: 300,
  });
  const [isSaving, setIsSaving] = React.useState(false);
  const [saveSuccess, setSaveSuccess] = React.useState(false);
  const [error, setError] = React.useState(null);

  // Fetch settings when component mounts or when expanded
  React.useEffect(() => {
    if (isExpanded) {
      fetchSettings();
    }
  }, [isExpanded]);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/settings");
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else {
        setError("Failed to load settings");
      }
    } catch (error) {
      console.error("Error fetching settings:", error);
      setError("Error loading settings");
    }
  };

  const handleSettingChange = (name, value) => {
    setSettings((prev) => ({
      ...prev,
      [name]: value,
    }));
    setSaveSuccess(false);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    setError(null);

    try {
      const response = await fetch("/api/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to save settings");
      }
    } catch (error) {
      console.error("Error saving settings:", error);
      setError("Error saving settings");
    } finally {
      setIsSaving(false);
    }
  };

  const togglePanel = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="card mb-4">
      <div
        className="card-header"
        onClick={togglePanel}
        style={{ cursor: "pointer" }}
      >
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i
              className={`bi bi-chevron-${isExpanded ? "down" : "right"} me-2`}
            ></i>
            <i className="bi bi-gear me-2"></i>
            Settings
          </h5>
        </div>
      </div>

      {isExpanded && (
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <div className="form-check form-switch">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="enable-summarization"
                  checked={settings.enable_summarization}
                  onChange={(e) =>
                    handleSettingChange(
                      "enable_summarization",
                      e.target.checked
                    )
                  }
                />
                <label
                  className="form-check-label"
                  htmlFor="enable-summarization"
                >
                  Enable AI Summarization
                </label>
              </div>
              <small className="text-muted d-block mt-1">
                <i className="bi bi-info-circle me-1"></i>
                Enabling summarization requires high processing power as it uses
                DeepSeek R1 1.5B locally on your PC.
              </small>
            </div>

            <div className="mb-3">
              <label htmlFor="capture-interval" className="form-label">
                Screenshot Capture Interval (seconds)
              </label>
              <input
                type="number"
                className="form-control"
                id="capture-interval"
                min="10"
                max="3600"
                value={settings.capture_interval}
                onChange={(e) =>
                  handleSettingChange(
                    "capture_interval",
                    parseInt(e.target.value)
                  )
                }
              />
              <small className="text-muted">
                Default: 300 seconds (5 minutes). Minimum: 10 seconds.
              </small>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSaving}
            >
              {isSaving ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  Saving...
                </>
              ) : (
                "Save Settings"
              )}
            </button>

            {saveSuccess && (
              <div className="alert alert-success mt-3">
                Settings saved successfully!
              </div>
            )}

            {error && <div className="alert alert-danger mt-3">{error}</div>}
          </form>
        </div>
      )}
    </div>
  );
};
