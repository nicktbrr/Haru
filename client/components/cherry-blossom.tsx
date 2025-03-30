import { CherryBlossomFull, CherryBlossomPetal, CherryBlossomSimple } from "./cherry-blossom-icons"

type CherryBlossomProps = {
  className?: string
  variant?: "full" | "petal" | "simple"
}

export function CherryBlossom({ className, variant = "full" }: CherryBlossomProps) {
  switch (variant) {
    case "full":
      return <CherryBlossomFull className={className} />
    case "petal":
      return <CherryBlossomPetal className={className} />
    case "simple":
      return <CherryBlossomSimple className={className} />
    default:
      return <CherryBlossomFull className={className} />
  }
}

