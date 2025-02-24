const ScreenshotGrid = ({
  screenshots,
  allTags,
  onToggleFavorite,
  onAddTag,
  onRemoveTag,
  currentPage,
  onPageChange,
  refetch,
}) => {
  const [selectedScreenshot, setSelectedScreenshot] = React.useState(null);
  const [selectedIndex, setSelectedIndex] = React.useState(-1);

  const handleScreenshotClick = (screenshot, index) => {
    setSelectedScreenshot(screenshot);
    setSelectedIndex(index);
  };

  const handleCloseModal = () => {
    setSelectedScreenshot(null);
    setSelectedIndex(-1);
  };

  const handlePrevious = async () => {
    if (selectedIndex > 0) {
      await refetch(); // Refetch before updating the view
      setSelectedScreenshot(screenshots.items[selectedIndex - 1]);
      setSelectedIndex(selectedIndex - 1);
    }
  };

  const handleNext = async () => {
    if (selectedIndex < screenshots.items.length - 1) {
      await refetch(); // Refetch before updating the view
      setSelectedScreenshot(screenshots.items[selectedIndex + 1]);
      setSelectedIndex(selectedIndex + 1);
    }
  };

  React.useEffect(() => {
    console.log(screenshots);
    if (selectedScreenshot) {
      const updatedScreenshot = screenshots.items.find(
        (s) => s.id === selectedScreenshot.id
      );
      if (updatedScreenshot) {
        setSelectedScreenshot(updatedScreenshot);
      }
    }
  }, [screenshots]);

  return (
    <div>
      <div className="row g-4">
        {screenshots.items.map((screenshot, index) => (
          <div key={screenshot.id} className="col-md-3">
            <div className="card h-100">
              <img
                src={`/data/screenshots/${screenshot.file_path}`}
                className="card-img-top cursor-pointer"
                alt="Screenshot"
                onClick={() => handleScreenshotClick(screenshot, index)}
              />
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-start">
                  <h6 className="card-title mb-2">{screenshot.app_name}</h6>
                  <span
                    className="favorite-icon"
                    onClick={async () => {
                      await onToggleFavorite(screenshot.id);
                      refetch();
                    }}
                    style={{ cursor: "pointer" }}
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
                      className="badge bg-secondary me-1"
                      onClick={async () => {
                        await onRemoveTag(screenshot.id, tag.id);
                        refetch();
                      }}
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
                          (tag) => !screenshot.tags.some((t) => t.id === tag.id)
                        )
                        .map((tag) => (
                          <li key={tag.id}>
                            <button
                              className="dropdown-item"
                              onClick={async () => {
                                await onAddTag(screenshot.id, tag.id);
                                refetch();
                              }}
                            >
                              {tag.name}
                            </button>
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

      {screenshots.pages > 1 && (
        <nav className="mt-4">
          <ul className="pagination justify-content-center">
            {Array.from({ length: screenshots.pages }, (_, i) => (
              <li
                key={i + 1}
                className={`page-item ${currentPage === i + 1 ? "active" : ""}`}
              >
                <button
                  className="page-link"
                  onClick={() => onPageChange(i + 1)}
                >
                  {i + 1}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}

      {selectedScreenshot && (
        <ScreenshotModal
          screenshot={selectedScreenshot}
          onClose={handleCloseModal}
          onPrevious={handlePrevious}
          onNext={handleNext}
          onToggleFavorite={async (id) => {
            await onToggleFavorite(id);
            refetch();
          }}
          onAddTag={async (id, tagId) => {
            await onAddTag(id, tagId);
            refetch();
          }}
          onRemoveTag={async (id, tagId) => {
            await onRemoveTag(id, tagId);
            refetch();
          }}
          allTags={allTags}
          isFirst={selectedIndex === 0}
          isLast={selectedIndex === screenshots.items.length - 1}
          refetch={refetch}
        />
      )}
    </div>
  );
};
