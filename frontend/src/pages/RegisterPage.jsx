import { useState } from "react";

import { registerUser } from "../services/authService";


function RegisterPage({ onRegistered, onBackToLogin }) {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");


    async function handleSubmit(event) {
        event.preventDefault();

        setLoading(true);
        setError("");
        setSuccess("");

        try {
            await registerUser({
                name,
                email,
                password,
            });

            setSuccess(
                "Registration successful. You can now sign in."
            );

            setTimeout(() => {
                onRegistered();
            }, 800);

        } catch (requestError) {
            setError(
                requestError.message ||
                "Registration failed."
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
                    Create Account
                </h1>

                <p>
                    Create an account to use the
                    AI Dataset Labeling Marketplace.
                </p>


                <form onSubmit={handleSubmit}>

                    <label htmlFor="name">
                        Name
                    </label>

                    <input
                        id="name"
                        type="text"
                        value={name}
                        onChange={(event) =>
                            setName(event.target.value)
                        }
                        placeholder="Your name"
                        minLength={2}
                        maxLength={100}
                        required
                    />


                    <label htmlFor="email">
                        Email
                    </label>

                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) =>
                            setEmail(event.target.value)
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
                            setPassword(event.target.value)
                        }
                        placeholder="Minimum 8 characters"
                        minLength={8}
                        maxLength={128}
                        required
                    />


                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}


                    {success && (
                        <div className="success-message">
                            {success}
                        </div>
                    )}


                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Creating Account..."
                            : "Create Account"}
                    </button>

                </form>


                <button
                    type="button"
                    className="secondary-button"
                    onClick={onBackToLogin}
                >
                    Back to Login
                </button>

            </section>

        </main>
    );
}


export default RegisterPage;