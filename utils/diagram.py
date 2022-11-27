import math

FG_COLORS = "bg_0 bg_1 bg_2 red orange yellow green cyan blue violet magenta dim_0 fg_0 fg_1".split()


def fg_colors(palette):
    return [color for name, color in palette.items() if name in FG_COLORS]


def bg_colors(palette):
    return [color for name, color in palette.items() if name in ("bg_0", "fg_0")]


def lab_l(color):
    return int(round(color.lab.lab_l))


class Diagram:
    def __init__(
        self,
        width=1000,
        height=600,
        square_size=48,
        line_width=3,
        margin=125,
        adjust_alignement=False,
    ):
        self.width = width
        self.height = height
        self.square_size = square_size
        self.square_half = square_size / 2
        self.line_width = line_width
        self.margin = margin
        self.image_width = width + margin + line_width
        self.image_height = height + margin * 1.5
        self.adj_x = self.line_width if adjust_alignement else 0
        self.adj_y = (self.square_half * 0.4) if adjust_alignement else 0

    def pick_constrasting_share(self, luminance, bg_colors):
        bg, fg = bg_colors
        if luminance > (lab_l(fg) + lab_l(bg)) / 2:
            return str(bg.srgb)
        return str(fg.srgb)

    def draw_swatches(self, palette, out):
        bgcolors = bg_colors(palette)
        colors = fg_colors(palette)
        bg = palette["bg_0"]
        width, height, sqsize, sqhalf = (
            self.width,
            self.height,
            self.square_size,
            self.square_half,
        )
        print("      <g>", file=out)
        for i, color in enumerate(colors):
            luminance = lab_l(color)
            contrast = self.pick_constrasting_share(luminance, bgcolors)
            xcenter = (i + 1.7) * width / (len(colors) + 1.5)
            ycenter = luminance * height / 100.0
            print(
                f"""\
            <!-- group is translated to the center of square with some flipping for easier translation -->
            <g transform="scale(1,-1)
                          translate({xcenter:.1f},{ycenter:.1f})
                          scale(1,-1)
                          translate(0,{height:.0f})" >
                <g stroke="{bg.srgb}" stroke-width="{self.line_width:.1f}" >
                    <rect x="{-sqhalf:.1f}" y="{-sqhalf:.1f}" width="{sqsize:.1f}" height="{sqsize:.1f}"
                          fill="{color.srgb}" stroke="{bg.srgb}"
                          stroke-width="{self.line_width:.1f}" />
                </g>

                <text x="{self.adj_x:.1f}" y="{self.adj_y:.1f}" fill="{contrast}"
                      text-anchor="middle" dominant-baseline="central" >
                    {luminance}
                </text>

                <text x="{-sqsize*0.8:.1f}" y="{self.adj_y:.1f}"
                      fill="{color.srgb}"
                      text-anchor="end"
                      dominant-baseline="central"
                      font-weight="bold"
                      transform="rotate(-90)" >
                    { color.name }
                </text>
            </g>""",
                file=out,
            )
        print("      </g>", file=out)

    def draw_background(self, palette, out):
        colors = bg_colors(palette)
        colors = sorted(colors, key=lambda c: lab_l(c))
        # we want the circles to have the same area as the squares
        radius = math.sqrt(4.0 / math.pi) * self.square_half
        height = self.height
        for color in colors:
            luminance = lab_l(color)
            contrast = self.pick_constrasting_share(luminance, colors)
            print(
                f"""\
        <rect x="0" y="0"
              width="{self.width:.0f}"
              height="{((100-luminance)/100.0)*height:.1f}"
              fill="{color.srgb}" />
        <circle cx="0" cy="{((100-luminance)/100.0)*height:.1f}"
                r="{radius:.1f}"
                fill="{color.srgb}"
                stroke="#777"
                stroke-width="{self.line_width:.1f}" />
        <text x="{self.adj_x:.1f}" y="{((100-luminance)/100.0)*height + self.adj_y:.1f}"
              fill="{contrast}"
              text-anchor="middle" dominant-baseline="central" >
            { luminance }
        </text>
        <text x="{radius*1.3:.1f}" y="{((98-luminance)/100.0)*height:.1f}"
              fill="{contrast}"
              text-anchor="begin" >
            { color.name }
        </text>
""",
                file=out,
            )

    def draw_axis(self, out):
        axis_color = "#777"
        axisX = -self.square_size
        notch_half = self.square_half / 2.0
        print(
            f"""\
<defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{axis_color}" />
    </marker>
</defs>

<g stroke="{axis_color}" stroke-width="{self.line_width:.1f}" >
    <line x1="{axisX:.1f}" y1="{self.height+self.margin/4.0:.1f}"
          x2="{axisX:.1f}" y2="{-self.margin/4.0:.1f}"
          marker-end="url(#arrowhead)" />
    <line x1="{axisX-notch_half:.1f}" y1="0"
          x2="{axisX+notch_half:.1f}" y2="0" />
    <line x1="{axisX-notch_half:.1f}" y1="{self.height}"
          x2="{axisX+notch_half:.1f}" y2="{self.height}" />
</g>

<text x="{axisX-1.5*notch_half}" y="{self.height + self.adj_y}"
      text-anchor="end" dominant-baseline="central"
      fill="{axis_color}" > 0 </text>
<text x="{axisX-1.5*notch_half}" y="{self.adj_y}"
      text-anchor="end" dominant-baseline="central"
      fill="{axis_color}" > 100 </text>
<g transform="translate({axisX-notch_half},{self.height/2.0})" >
    <text x="0" y="0"
          text-anchor="middle"
          transform="rotate(-90)"
          fill="{axis_color}" > luminance </text>
</g>""",
            file=out,
        )

    def write(self, palette, out):
        print("""<?xml version="1.0" encoding="UTF-8"?>""", file=out)
        width, height, line_width, margin = (
            self.width,
            self.height,
            self.line_width,
            self.margin,
        )
        print(
            f"""\
<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:svg="http://www.w3.org/2000/svg"
     width="{self.image_width:.0f}"
     height="{self.image_height:.0f}"
     font-family="Signika, sans"
     font-size="{0.65*self.square_size:.1f}px" >
    <style>
        @font-face {{
            font-family: 'Signika';
            font-style: normal;
            font-weight: 400;
            src: local('Signika'), local('Signika-Regular'),
              url(https://fonts.gstatic.com/s/signika/v6/q41y_9MUP_N8ipOH4ORRvw.woff2) format('woff2');
            unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02C6, U+02DA, U+02DC,
              U+2000-206F, U+2074, U+20AC, U+2212, U+2215, U+E0FF, U+EFFD, U+F000;
        }}
        @font-face {{
            font-family: 'Signika';
            font-style: normal;
            font-weight: 700;
            src: local('Signika-Bold'),
              url(https://fonts.gstatic.com/s/signika/v6/7M5kxD4eGxuhgFaIk95pBfk_vArhqVIZ0nv9q090hN8.woff2) format('woff2');
            unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02C6, U+02DA, U+02DC,
              U+2000-206F, U+2074, U+20AC, U+2212, U+2215, U+E0FF, U+EFFD, U+F000;
        }}
    </style>
    <g transform="translate({margin},{margin})" >
        <text x="{width*0.5:.1f}" y="{self.adj_y/0.65 - margin*0.5:.1f}"
              text-anchor="middle" dominant-baseline="central"
              font-size="{self.square_size:0.1f}px" fill="#777" >
            { palette['name'] }
        </text>
        <rect x="{-line_width/2.0:.1f}" y="{-line_width/2.0:.1f}"
              width="{width+line_width:.1f}" height="{height+line_width:.1f}"
              fill="#777" />
        <rect x="0" y="0" width="{width}" height="{height}" fill="#000" />
""",
            file=out,
        )
        self.draw_axis(out)
        self.draw_background(palette, out)
        self.draw_swatches(palette, out)
        print("      </g>", file=out)
        print("   </svg>", file=out)
