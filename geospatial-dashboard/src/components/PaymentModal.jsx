// src/components/PaymentModal.jsx
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PaymentModal = ({ isOpen, onClose, onPayment, user }) => {
  const [processing, setProcessing] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState("monthly");

  const handlePayment = async () => {
    if (!user) {
      return;
    }

    setProcessing(true);

    try {
      // Call the backend upgrade API
      const response = await fetch(
        "http://localhost:8000/api/v1/user/upgrade",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": user.api_key || "premium_user_key_001", // Use user's API key if available
          },
          body: JSON.stringify({
            user_id: user.user_id,
            plan_type: selectedPlan,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Upgrade failed");
      }

      const result = await response.json();

      // Update user status in parent component
      onPayment({ ...user, subscription_status: "premium" });
      onClose();
    } catch (error) {
      console.error("Payment error:", error);
      alert("Payment failed. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
      <Card className="w-96 shadow-2xl">
        <CardHeader>
          <CardTitle>Upgrade to Premium</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-muted-foreground">
              Unlock unlimited geospatial analysis and advanced features
            </p>

            {/* Plan Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Plan:</label>
              <div className="space-y-2">
                <div
                  className={`p-3 border rounded cursor-pointer ${
                    selectedPlan === "monthly"
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200"
                  }`}
                  onClick={() => setSelectedPlan("monthly")}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Monthly Plan</span>
                    <span className="text-lg font-bold text-green-600">
                      $29/mo
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    Perfect for trying premium features
                  </p>
                </div>
                <div
                  className={`p-3 border rounded cursor-pointer ${
                    selectedPlan === "yearly"
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200"
                  }`}
                  onClick={() => setSelectedPlan("yearly")}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Yearly Plan</span>
                    <span className="text-lg font-bold text-green-600">
                      $299/yr
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">
                    Save $49/year - Best value!
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-muted p-3 rounded-md">
              <h3 className="font-semibold text-sm mb-2">Premium Features:</h3>
              <ul className="text-xs text-muted-foreground space-y-1">
                <li>• Unlimited data requests</li>
                <li>• High-resolution downloads</li>
                <li>• Priority processing</li>
                <li>• API access</li>
                <li>• Historical data access</li>
              </ul>
            </div>

            <div className="p-3 border rounded-md bg-blue-50">
              <p className="text-sm text-muted-foreground mb-1">
                Demo Payment Card
              </p>
              <p className="text-xs font-mono">**** **** **** 4242</p>
              <p className="text-xs text-muted-foreground">
                Exp: 12/25 | CVV: 123
              </p>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={onClose} disabled={processing}>
                Cancel
              </Button>
              <Button
                onClick={handlePayment}
                disabled={processing}
                className="min-w-[100px]"
              >
                {processing ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span className="ml-2">Processing...</span>
                  </div>
                ) : (
                  "Pay Now"
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentModal;
