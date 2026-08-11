import { useState } from "react";
import { loginUser } from "../services/authService";


function LoginPage({ onLogin, onRegister }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    async function handleSubmit(event) {
        event.preventDefault();

        setLoading(true);
        setError("");

        try {
            await loginUser({
                email,
                password,
            });

            onLogin();
        } catch (requestError) {
            setError(
                requestError.message ||
                "Login failed."
            );
        } finally {
            setLoading(false);
        }
    }


    return (
        <main className="auth-page">
            <section className="auth-card">

                <div className="brand-mark">
                    AI
                </div>

                <h1>
                    AI Dataset Marketplace
                </h1>

                <p>
                    Sign in to manage datasets
                    and labeling jobs.
                </p>


                <form onSubmit={handleSubmit}>

                    <label htmlFor="email">
                        Email
                    </label>

                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) =>
                            setEmail(
                                event.target.value
                            )
                        }
                        placeholder="you@example.com"
                        required
                    />


                    <label htmlFor="password">
                        Password
                    </label>

                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) =>
                            setPassword(
                                event.target.value
                            )
                        }
                        placeholder="Enter your password"
                        required
                    />


                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}


                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Signing in..."
                            : "Sign In"}
                    </button>

                </form>
<div className="auth-divider">
    Don't have an account?
</div>

<button
    type="button"
    className="secondary-button"
    onClick={onRegister}
>
    Create Account
</button>
            </section>
        </main>
    );
}


export default LoginPage;