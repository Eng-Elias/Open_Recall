const DeleteScreenshotsPanel = ({ onScreenshotsDeleted }) => {
  const [date, setDate] = React.useState("");
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [showConfirm, setShowConfirm] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [excludeFavorites, setExcludeFavorites] = React.useState(false);
  const [excludeWithNotes, setExcludeWithNotes] = React.useState(false);
  const [selectedTagId, setSelectedTagId] = React.useState("");
  const [tags, setTags] = React.useState([]);

  // Fetch tags when component mounts
  React.useEffect(() => {
    if (isExpanded) {
      fetchTags();
    }
  }, [isExpanded]);

  const fetchTags = async () => {
    try {
      const response = await fetch("/api/tags");
      if (response.ok) {
        const data = await response.json();
        setTags(data);
      }
    } catch (error) {
      console.error("Error fetching tags:", error);
    }
  };

  const handleDateChange = (e) => {
    setDate(e.target.value);
    setError(null);
    setResult(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate date
    if (!date) {
      setError("Please select a date");
      return;
    }

    // Show confirmation dialog
    setShowConfirm(true);
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    setError(null);
    setResult(null);

    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (excludeFavorites) params.append("exclude_favorites", "true");
      if (excludeWithNotes) params.append("exclude_with_notes", "true");
      if (selectedTagId) params.append("tag_id", selectedTagId);

      const queryString = params.toString() ? `?${params.toString()}` : "";

      const response = await fetch(
        `/api/screenshots/before-date/${date}${queryString}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        if (onScreenshotsDeleted) {
          onScreenshotsDeleted(data.count);
        }
      } else {
        setError(data.detail || "Failed to delete screenshots");
      }
    } catch (error) {
      setError("An error occurred while deleting screenshots");
      console.error("Error deleting screenshots:", error);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirm(false);
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
            Delete Old Screenshots
          </h5>
        </div>
      </div>

      {isExpanded && (
        <div className="card-body">
          <p className="card-text text-muted">
            Delete all screenshots taken before a specific date. This action
            cannot be undone.
          </p>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="delete-date" className="form-label">
                Delete screenshots before:
              </label>
              <input
                type="date"
                id="delete-date"
                className={`form-control w-25 ${error ? "is-invalid" : ""}`}
                value={date}
                onChange={handleDateChange}
                max={new Date().toISOString().split("T")[0]}
              />
              {error && <div className="invalid-feedback">{error}</div>}
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="exclude-favorites"
                  checked={excludeFavorites}
                  onChange={(e) => setExcludeFavorites(e.target.checked)}
                />
                <label className="form-check-label" htmlFor="exclude-favorites">
                  Exclude favorite screenshots
                </label>
              </div>
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="exclude-with-notes"
                  checked={excludeWithNotes}
                  onChange={(e) => setExcludeWithNotes(e.target.checked)}
                />
                <label
                  className="form-check-label"
                  htmlFor="exclude-with-notes"
                >
                  Exclude screenshots with notes
                </label>
              </div>
            </div>

            <div className="mb-3">
              <label htmlFor="tag-filter" className="form-label">
                Only delete screenshots with tag:
              </label>
              <select
                id="tag-filter"
                className="form-select"
                value={selectedTagId}
                onChange={(e) => setSelectedTagId(e.target.value)}
              >
                <option value="">All tags (no filter)</option>
                {tags.map((tag) => (
                  <option key={tag.id} value={tag.id}>
                    {tag.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="btn btn-danger"
              disabled={isDeleting || !date}
            >
              Delete Screenshots
            </button>
          </form>

          {result && (
            <div className="alert alert-success mt-3">
              {result.message} ({result.files_deleted} files removed from disk)
            </div>
          )}
        </div>
      )}

      {/* Confirmation Modal - Using Bootstrap's modal with proper event handling */}
      {showConfirm && (
        <div
          className="modal"
          tabIndex="-1"
          role="dialog"
          style={{ display: "block", backgroundColor: "rgba(0,0,0,0.5)" }}
        >
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Deletion</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={handleCancelDelete}
                  disabled={isDeleting}
                ></button>
              </div>
              <div className="modal-body">
                <p>
                  Are you sure you want to delete all screenshots taken before{" "}
                  {date}?
                </p>
                <p>
                  {excludeFavorites && (
                    <span className="d-block">
                      • Favorite screenshots will be kept
                    </span>
                  )}
                  {excludeWithNotes && (
                    <span className="d-block">
                      • Screenshots with notes will be kept
                    </span>
                  )}
                  {selectedTagId && (
                    <span className="d-block">
                      • Only screenshots with the selected tag will be deleted
                    </span>
                  )}
                </p>
                <p className="text-danger fw-bold">
                  This action cannot be undone!
                </p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCancelDelete}
                  disabled={isDeleting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={handleConfirmDelete}
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <>
                      <span
                        className="spinner-border spinner-border-sm me-2"
                        role="status"
                        aria-hidden="true"
                      ></span>
                      Deleting...
                    </>
                  ) : (
                    "Delete"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
