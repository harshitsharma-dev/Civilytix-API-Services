// src/components/LoginModal.jsx
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const LoginModal = ({ isOpen, onClose, onLogin }) => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!email) {
      setError("Please enter an email address");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Call the backend login API
      const response = await fetch("http://localhost:8000/api/v1/user/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const userData = await response.json();

      // Pass user data to parent component
      onLogin(userData);
      onClose();
      setEmail("");
    } catch (error) {
      console.error("Login error:", error);
      setError("Login failed. Please check your email or try demo accounts.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (demoEmail) => {
    setEmail(demoEmail);
    setTimeout(handleSubmit, 100); // Small delay to let state update
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      handleSubmit();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
      <Card className="w-96 shadow-2xl">
        <CardHeader>
          <CardTitle>Login</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your email address"
                disabled={loading}
              />
            </div>

            <Button
              onClick={handleSubmit}
              className="w-full"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Login"}
            </Button>

            <div className="border-t pt-4">
              <p className="text-sm text-gray-600 mb-3">Demo Accounts:</p>
              <div className="space-y-2">
                <Button
                  onClick={() => handleDemoLogin("free2@example.com")}
                  variant="outline"
                  size="sm"
                  className="w-full text-left justify-start"
                  disabled={loading}
                >
                  🆓 Free User (free2@example.com)
                </Button>
                <Button
                  onClick={() => handleDemoLogin("premium1@example.com")}
                  variant="outline"
                  size="sm"
                  className="w-full text-left justify-start"
                  disabled={loading}
                >
                  ⭐ Premium User (premium1@example.com)
                </Button>
              </div>
            </div>

            <Button onClick={onClose} variant="outline" className="w-full">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginModal;
