"use client"

import { useEffect, useState } from "react"
import { CherryBlossomPetal, CherryBlossomSimple } from "./cherry-blossom-icons"

type Petal = {
  id: number
  left: number
  size: number
  delay: number
  duration: number
  rotation: number
  opacity: number
  type: "petal" | "simple"
}

type FallingPetalsProps = {
  count?: number
}

export function FallingPetals({ count = 20 }: FallingPetalsProps) {
  const [petals, setPetals] = useState<Petal[]>([])

  useEffect(() => {
    const newPetals: Petal[] = []

    for (let i = 0; i < count; i++) {
      newPetals.push({
        id: i,
        left: Math.random() * 100, // percentage across the screen
        size: Math.random() * 15 + 10, // size between 10-25px
        delay: Math.random() * 15, // delay up to 15s
        duration: Math.random() * 10 + 15, // animation duration between 15-25s
        rotation: Math.random() * 360, // initial rotation
        opacity: Math.random() * 0.3 + 0.2, // opacity between 0.2-0.5
        type: Math.random() > 0.7 ? "simple" : "petal", // 70% petals, 30% simple flowers
      })
    }

    setPetals(newPetals)
  }, [count])

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {petals.map((petal) => (
        <div
          key={petal.id}
          className="absolute top-0 animate-falling-petal"
          style={{
            left: `${petal.left}%`,
            width: `${petal.size}px`,
            height: `${petal.size}px`,
            animationDelay: `${petal.delay}s`,
            animationDuration: `${petal.duration}s`,
            transform: `rotate(${petal.rotation}deg)`,
            opacity: petal.opacity,
          }}
        >
          {petal.type === "petal" ? (
            <CherryBlossomPetal className="w-full h-full text-pink-300" />
          ) : (
            <CherryBlossomSimple className="w-full h-full text-pink-300" />
          )}
        </div>
      ))}
    </div>
  )
}

