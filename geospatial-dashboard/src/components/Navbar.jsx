// src/components/Navbar.jsx
import React from "react";
import { Button } from "@/components/ui/button";

const Navbar = ({ user, onLogin, onLogout, onUpgrade }) => {
  return (
    <nav className="bg-background border-b border-border p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold text-foreground">
        Geospatial Data Platform
      </h1>
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <span className="text-foreground">Welcome, {user.name}</span>
            <span
              className={`px-2 py-1 rounded text-xs ${
                user.paymentStatus === "paid"
                  ? "bg-green-100 text-green-800 border border-green-200"
                  : "bg-orange-100 text-orange-800 border border-orange-200"
              }`}
            >
              {user.paymentStatus === "paid" ? "Premium" : "Free"}
            </span>
            {user.paymentStatus !== "paid" && (
              <Button onClick={onUpgrade} variant="default">
                Upgrade
              </Button>
            )}
            <Button onClick={onLogout} variant="destructive">
              Logout
            </Button>
          </>
        ) : (
          <Button onClick={onLogin} variant="default">
            Login
          </Button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
