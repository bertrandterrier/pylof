#let ttl(s) = [#h(3pt)#smallcaps(
  text(
    s,
    tracking: 1pt,
  )
)#h(3pt)]

#let n(s) = [#emph([#upper(
  s.at(0)
)#lower(
    s.slice(1)
  )])]
#let pylof = [#ttl("PyLoF")]
#let kmark = [#ttl("kMark")]

#set page(
  paper: "a4",
  margin: 30mm,
  header: [#v(1fr)PyLoF]
)

#set text(
  font: "Linux Libertine",
  size: 12pt,
  lang: "en"
)

#set par(
  justify: true,
)


#align(center)[#set par(justify: false)
  #block(width: 70%)[#align(
  center+top, [#text(
    size: 18pt,
    weight: "bold",
  )[#pylof]

  #text(
    size: 18pt,
    style: "normal",
    weight: "regular",
    hyphenate: false,
    tracking: 1pt
  )[#smallcaps([A _kMark_ parser based on _Python_])]

  #emph([by bertrandterrier])
  ])]]


