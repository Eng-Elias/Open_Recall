const ScreenshotModal = ({
  screenshot,
  onClose,
  onNext,
  onPrevious,
  onToggleFavorite,
  onAddTag,
  onRemoveTag,
  allTags,
  isFirst,
  isLast,
}) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const handleKeyPress = (e) => {
    if (e.key === "ArrowLeft") {
      onPrevious();
    } else if (e.key === "ArrowRight") {
      onNext();
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  React.useEffect(() => {
    document.addEventListener("keydown", handleKeyPress);
    return () => {
      document.removeEventListener("keydown", handleKeyPress);
    };
  }, []);

  if (!screenshot) return null;

  return (
    <div className="modal show d-block" tabIndex="-1">
      <div className="modal-dialog modal-xl modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <div className="d-flex justify-content-between align-items-center w-100">
              <div className="d-flex align-items-center gap-3">
                <h5 className="modal-title mb-0">{screenshot.app_name}</h5>
                <span className="text-muted">{formatDate(screenshot.timestamp)}</span>
              </div>
              <div className="d-flex align-items-center gap-3">
                <div className="tags-container">
                  {screenshot.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="badge bg-secondary me-1"
                      onClick={() => onRemoveTag(screenshot.id, tag.id)}
                      style={{ cursor: "pointer" }}
                    >
                      {tag.name} ×
                    </span>
                  ))}
                  <div className="dropdown d-inline-block">
                    <button
                      className="btn btn-sm btn-outline-secondary dropdown-toggle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      + Add Tag
                    </button>
                    <ul className="dropdown-menu">
                      {allTags
                        .filter(
                          (tag) =>
                            !screenshot.tags.some((t) => t.id === tag.id)
                        )
                        .map((tag) => (
                          <li key={tag.id}>
                            <button
                              className="dropdown-item"
                              onClick={() => onAddTag(screenshot.id, tag.id)}
                            >
                              {tag.name}
                            </button>
                          </li>
                        ))}
                    </ul>
                  </div>
                </div>
                <span
                  className="favorite-icon"
                  onClick={() => onToggleFavorite(screenshot.id)}
                  style={{ cursor: "pointer" }}
                >
                  {screenshot.is_favorite ? "★" : "☆"}
                </span>
                <button
                  type="button"
                  className="btn-close"
                  onClick={onClose}
                ></button>
              </div>
            </div>
          </div>
          <div className="modal-body position-relative p-0">
            <div className="navigation-overlay">
              <button
                className="btn btn-light btn-lg navigation-btn left"
                onClick={onPrevious}
                disabled={isFirst}
              >
                ←
              </button>
              <button
                className="btn btn-light btn-lg navigation-btn right"
                onClick={onNext}
                disabled={isLast}
              >
                →
              </button>
            </div>
            <img
              src={`/data/screenshots/${screenshot.file_path}`}
              className="img-fluid w-100"
              alt="Screenshot"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
