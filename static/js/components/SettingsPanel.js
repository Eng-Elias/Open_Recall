const SettingsPanel = () => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [settings, setSettings] = React.useState({
    enable_summarization: false,
    capture_interval: 300,
    summarization_model: "Qwen/Qwen2.5-0.5B",
  });
  const [isSaving, setIsSaving] = React.useState(false);
  const [saveSuccess, setSaveSuccess] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [availableModels, setAvailableModels] = React.useState([]);
  const [isLoadingModels, setIsLoadingModels] = React.useState(false);
  const [isDownloadingModel, setIsDownloadingModel] = React.useState(false);
  const [downloadingModelId, setDownloadingModelId] = React.useState(null);

  // Fetch settings when component mounts or when expanded
  React.useEffect(() => {
    if (isExpanded) {
      fetchSettings();
      fetchAvailableModels();

      // Set up a timer to refresh model status every 5 seconds while downloading
      const intervalId = setInterval(() => {
        if (isDownloadingModel) {
          fetchAvailableModels();
        }
      }, 5000);

      // Clean up the interval when component unmounts or collapses
      return () => clearInterval(intervalId);
    }
  }, [isExpanded, isDownloadingModel]);

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

  const fetchAvailableModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch("/api/summarization/models");
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data);
      } else {
        console.error("Failed to load models");
      }
    } catch (error) {
      console.error("Error fetching models:", error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const handleSettingChange = (name, value) => {
    setSettings((prev) => ({
      ...prev,
      [name]: value,
    }));

    // If changing model, check if it's downloaded
    if (name === "summarization_model") {
      const selectedModel = availableModels.find((model) => model.id === value);
      if (selectedModel && !selectedModel.downloaded) {
        // Show a confirmation dialog
        if (
          window.confirm(
            `The model "${selectedModel.name}" is not downloaded yet. Do you want to download it now?`
          )
        ) {
          handleDownloadModel(value);
        }
      }
    }

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

  const handleDownloadModel = async (modelId) => {
    setIsDownloadingModel(true);
    setDownloadingModelId(modelId);
    try {
      const response = await fetch(
        `/api/summarization/models/${encodeURIComponent(modelId)}/download`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to download model");
      }
    } catch (error) {
      console.error("Error downloading model:", error);
      setError("Error downloading model");
    } finally {
      setIsDownloadingModel(false);
      setDownloadingModelId(null);
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
                language models locally on your PC.
              </small>
            </div>

            <div className="mb-3">
              <label htmlFor="summarization-model" className="form-label">
                Summarization Model
              </label>
              <select
                className="form-select"
                id="summarization-model"
                value={settings.summarization_model}
                onChange={(e) =>
                  handleSettingChange("summarization_model", e.target.value)
                }
              >
                {availableModels.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name} {model.downloaded ? "✓" : ""}
                  </option>
                ))}
              </select>
              <small className="text-muted d-block mt-1">
                <i className="bi bi-info-circle me-1"></i>
                Select the model to use for summarization. Models need to be
                downloaded before use.
              </small>
            </div>

            {/* Model download section */}
            <div className="mb-4">
              <h6>Available Models</h6>
              {isLoadingModels ? (
                <div className="text-center p-3">
                  <div
                    className="spinner-border spinner-border-sm"
                    role="status"
                  >
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <span className="ms-2">Loading models...</span>
                </div>
              ) : (
                <div className="list-group">
                  {availableModels.map((model) => (
                    <div
                      key={model.id}
                      className="list-group-item d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <div className="fw-bold">{model.name}</div>
                        <small className="text-muted">
                          {model.description}
                        </small>
                      </div>
                      <div>
                        {model.downloaded ? (
                          <span className="badge bg-success">Downloaded</span>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleDownloadModel(model.id)}
                            disabled={isDownloadingModel}
                          >
                            {isDownloadingModel &&
                            downloadingModelId === model.id ? (
                              <>
                                <span
                                  className="spinner-border spinner-border-sm me-1"
                                  role="status"
                                  aria-hidden="true"
                                ></span>
                                Downloading...
                              </>
                            ) : (
                              <>
                                <i className="bi bi-download me-1"></i>
                                Download
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
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
