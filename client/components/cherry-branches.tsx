import { CherryBlossomFull, CherryBlossomSimple } from "./cherry-blossom-icons"

export function CherryBranchLeft({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 200" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10,100 Q50,60 100,80 T180,50" stroke="currentColor" strokeWidth="4" fill="none" />
      <foreignObject x="35" y="75" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="45" y="65" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="55" y="70" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="40" y="80" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="50" y="75" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>

      <foreignObject x="115" y="60" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="125" y="55" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="135" y="50" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="120" y="50" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="130" y="45" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
    </svg>
  )
}

export function CherryBranchRight({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 200" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M190,100 Q150,60 100,80 T20,50" stroke="currentColor" strokeWidth="4" fill="none" />
      <foreignObject x="155" y="75" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="145" y="65" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="135" y="70" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="150" y="80" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="140" y="75" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>

      <foreignObject x="75" y="60" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="65" y="55" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="55" y="50" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="70" y="50" width="20" height="20">
        <CherryBlossomFull className="w-full h-full text-pink-400" />
      </foreignObject>
      <foreignObject x="60" y="45" width="20" height="20">
        <CherryBlossomSimple className="w-full h-full text-pink-400" />
      </foreignObject>
    </svg>
  )
}

