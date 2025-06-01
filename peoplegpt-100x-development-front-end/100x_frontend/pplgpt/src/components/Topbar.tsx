import { Link, useNavigate } from "react-router-dom";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { Button } from "./ui/button";
import { useCallback } from "react";
import { captureEvent } from "@/lib/posthog";

interface TopbarProps {
  className?: string;
}

export function Topbar({ className }: TopbarProps) {
  const navigate = useNavigate();

  const handleNavigation = useCallback(
    (path: string, pageName: string) => {
      captureEvent("navigation_clicked", {
        destination: pageName,
        path: path,
      });
      navigate(path);
    },
    [navigate]
  );

  return (
    <nav
      className={`flex items-center justify-between p-4 bg-white shadow-md ${
        className || ""
      }`}
    >
      {/* Left: Logo */}
      <div className="flex items-center space-x-2">
        <Link to="/" onClick={() => handleNavigation("/", "Home")}>
          <img src="/logo.png" alt="Logo" className="h-8" />
        </Link>
        <Link to="/" onClick={() => handleNavigation("/", "Home")}>
          <span className="text-xl font-semibold">PeopleGPT</span>
        </Link>
      </div>

      {/* Center: Navigation Links */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          onClick={() => handleNavigation("/analytics", "Analytics")}
        >
          Analytics
        </Button>
        <Button
          variant="ghost"
          onClick={() => handleNavigation("/history", "History")}
        >
          History
        </Button>
      </div>

      {/* Right: Search Bar */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search..."
          className="pl-10 pr-4 py-2 border rounded-lg w-64"
        />
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
      </div>
    </nav>
  );
}
