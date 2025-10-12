"use client"

import React, { useEffect, useState } from "react"
import { Sun, Moon } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const [isDark, setIsDark] = useState<boolean | null>(null)

  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      const saved = window.localStorage.getItem("theme")
      if (saved === "dark") {
        document.documentElement.classList.add("dark")
        setIsDark(true)
        return
      }

      if (saved === "light") {
        document.documentElement.classList.remove("dark")
        setIsDark(false)
        return
      }

      const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches
      if (prefersDark) {
        document.documentElement.classList.add("dark")
        setIsDark(true)
      } else {
        document.documentElement.classList.remove("dark")
        setIsDark(false)
      }
    } catch (e) {
      setIsDark(false)
    }
  }, [])

  const toggle = () => {
    try {
      const nowDark = document.documentElement.classList.toggle("dark")
      window.localStorage.setItem("theme", nowDark ? "dark" : "light")
      setIsDark(nowDark)
    } catch (e) {
      // noop
    }
  }

  // Use the existing Button component so styles align with the design system.
  // When dark mode is active show a filled primary-ish state; otherwise show ghost.
  const variant = isDark ? "default" : "ghost"

  return (
    <Button
      aria-pressed={!!isDark}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      title={isDark ? "Warehouse Floor Mode (dark) — click to switch" : "Light Mode — click to switch"}
      onClick={toggle}
      variant={variant as any}
      size="icon"
    >
      {isDark ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
    </Button>
  )
}
