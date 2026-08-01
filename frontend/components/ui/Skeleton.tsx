"use client";

interface SkeletonProps {
  className?: string;
  count?: number;
}

export default function Skeleton({ className = "h-12 w-full", count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`${className} bg-border rounded-lg animate-pulse`}
        />
      ))}
    </>
  );
}
