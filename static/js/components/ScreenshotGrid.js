const ScreenshotGrid = ({
  screenshots,
  allTags,
  onToggleFavorite,
  onAddTag,
  onRemoveTag,
  currentPage,
  onPageChange,
}) => {
  console.log(screenshots);
  return (
    <div>
      <div className="row g-4">
        {screenshots?.items?.map((screenshot) => (
          <div key={screenshot.id} className="col-md-4">
            <div className="card screenshot-card">
              <img
                src={`/assets/${screenshot.file_path}`}
                className="card-img-top"
                alt="Screenshot"
              />
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <h6 className="card-title">{screenshot.app_name}</h6>
                  <span
                    className={`favorite-icon`}
                    onClick={() => onToggleFavorite(screenshot.id)}
                  >
                    {screenshot.is_favorite ? "★" : "☆"}
                  </span>
                </div>
                <p className="card-text small text-muted">
                  {new Date(screenshot.timestamp).toLocaleString()}
                </p>
                <div className="tags-container">
                  {screenshot.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="badge bg-secondary me-1 mb-1"
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
                            !screenshot.tags.some(
                              (screenshotTag) => screenshotTag.id === tag.id
                            )
                        )
                        .map((tag) => (
                          <li key={tag.id}>
                            <a
                              className="dropdown-item"
                              href="#"
                              onClick={(e) => {
                                e.preventDefault();
                                onAddTag(screenshot.id, tag.id);
                              }}
                            >
                              {tag.name}
                            </a>
                          </li>
                        ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {screenshots && screenshots.pages > 1 && (
        <nav className="mt-4">
          <ul className="pagination justify-content-center">
            <li
              className={`page-item ${
                screenshots.page === 1 ? "disabled" : ""
              }`}
            >
              <button
                className="page-link"
                onClick={() => onPageChange(screenshots.page - 1)}
                disabled={screenshots.page === 1}
              >
                Previous
              </button>
            </li>
            {[...Array(screenshots.pages)].map((_, i) => (
              <li
                key={i + 1}
                className={`page-item ${
                  screenshots.page === i + 1 ? "active" : ""
                }`}
              >
                <button
                  className="page-link"
                  onClick={() => onPageChange(i + 1)}
                >
                  {i + 1}
                </button>
              </li>
            ))}
            <li
              className={`page-item ${
                screenshots.page === screenshots.pages ? "disabled" : ""
              }`}
            >
              <button
                className="page-link"
                onClick={() => onPageChange(screenshots.page + 1)}
                disabled={screenshots.page === screenshots.pages}
              >
                Next
              </button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );
};
