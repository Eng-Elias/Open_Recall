const DeleteScreenshotsPanel = ({ onScreenshotsDeleted }) => {
  const [date, setDate] = React.useState("");
  const [isDeleting, setIsDeleting] = React.useState(false);
  const [showConfirm, setShowConfirm] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [isExpanded, setIsExpanded] = React.useState(false);

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
      const response = await fetch(`/api/screenshots/before-date/${date}`, {
        method: "DELETE"
      });
      
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
      <div className="card-header" onClick={togglePanel} style={{ cursor: 'pointer' }}>
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i className={`bi bi-chevron-${isExpanded ? 'down' : 'right'} me-2`}></i>
            Delete Old Screenshots
          </h5>
        </div>
      </div>
      
      {isExpanded && (
        <div className="card-body">
          <p className="card-text text-muted">
            Delete all screenshots taken before a specific date. This action cannot be undone.
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="delete-date" className="form-label">
                Delete screenshots before:
              </label>
              <input
                type="date"
                id="delete-date"
                className={`form-control ${error ? "is-invalid" : ""}`}
                value={date}
                onChange={handleDateChange}
                max={new Date().toISOString().split("T")[0]}
              />
              {error && <div className="invalid-feedback">{error}</div>}
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
          style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}
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
                <p>Are you sure you want to delete all screenshots taken before {date}?</p>
                <p className="text-danger fw-bold">This action cannot be undone!</p>
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
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
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
