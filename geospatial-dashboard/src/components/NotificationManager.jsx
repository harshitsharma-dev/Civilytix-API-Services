// src/components/NotificationManager.jsx
import React, { useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { X, CheckCircle, XCircle, AlertTriangle, Info } from "lucide-react";

const NotificationManager = ({ notifications, onRemove }) => {
  return (
    <div className="fixed top-20 right-4 z-[9998] space-y-2 max-w-sm">
      {notifications.map((notif) => (
        <Notification key={notif.id} notification={notif} onRemove={onRemove} />
      ))}
    </div>
  );
};

const Notification = ({ notification, onRemove }) => {
  const { id, message, type } = notification;

  useEffect(() => {
    const timer = setTimeout(() => {
      onRemove(id);
    }, 5000);

    return () => clearTimeout(timer);
  }, [id, onRemove]);

  const getVariant = () => {
    switch (type) {
      case "success":
        return "success";
      case "error":
        return "destructive";
      case "warning":
        return "warning";
      case "info":
      default:
        return "info";
    }
  };

  const getIcon = () => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-4 w-4" />;
      case "error":
        return <XCircle className="h-4 w-4" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4" />;
      case "info":
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  return (
    <Alert
      variant={getVariant()}
      className="animate-in slide-in-from-right-full duration-300"
    >
      {getIcon()}
      <div className="flex items-start justify-between w-full">
        <AlertDescription className="flex-1">{message}</AlertDescription>
        <Button
          variant="ghost"
          size="sm"
          className="h-auto p-1 ml-2 hover:bg-transparent"
          onClick={() => onRemove(id)}
          aria-label="Close notification"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Progress bar for auto-dismiss */}
      <div className="mt-2 w-full bg-black/10 rounded-full h-1">
        <div
          className="bg-current rounded-full h-1"
          style={{
            animation: "shrink 5s linear forwards",
          }}
        />
      </div>

      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </Alert>
  );
};

export default NotificationManager;
