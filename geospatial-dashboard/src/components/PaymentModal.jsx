// src/components/PaymentModal.jsx
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PaymentModal = ({ isOpen, onClose, onPayment }) => {
  const [processing, setProcessing] = useState(false);

  const handlePayment = async () => {
    setProcessing(true);
    // Simulate payment processing delay
    setTimeout(() => {
      onPayment();
      setProcessing(false);
      onClose();
    }, 2000);
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
              Unlock unlimited data requests and downloads
            </p>
            <div className="text-2xl font-bold text-green-600">$50.00 USD</div>

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
