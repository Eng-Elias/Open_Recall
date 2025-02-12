function App() {
    const [message, setMessage] = React.useState("Welcome to FastAPI + React!");

    return (
        <div className="container py-5">
            <div className="row justify-content-center">
                <div className="col-md-8">
                    <div className="card shadow">
                        <div className="card-body">
                            <h1 className="text-center mb-4">{message}</h1>
                            <div className="d-flex justify-content-center">
                                <button
                                    className="btn btn-primary"
                                    onClick={() => setMessage("Button clicked!")}>
                                    Click Me
                                </button>
                            </div>
                            <div className="row mt-4">
                                <div className="col-md-6">
                                    <div className="card">
                                        <div className="card-body">
                                            <h5 className="card-title">Feature 1</h5>
                                            <p className="card-text">This is a sample feature card using Bootstrap styling.</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-6">
                                    <div className="card">
                                        <div className="card-body">
                                            <h5 className="card-title">Feature 2</h5>
                                            <p className="card-text">Another feature card showcasing Bootstrap's card component.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
