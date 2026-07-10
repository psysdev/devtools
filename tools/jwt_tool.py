"""JWT Decoder — decode JWT tokens and display header/payload."""

import sys
import json
import base64
from tools._base import Tool, P_JWT


def decode_jwt_part(part: str) -> dict:
    """Decode a base64url-encoded JWT part."""
    padding = 4 - len(part) % 4
    if padding != 4:
        part += "=" * padding
    return json.loads(base64.urlsafe_b64decode(part))


class JWTTool(Tool):
    name = "jwt"
    description = "Decode JWT tokens without verification"
    category = "utility"
    priority = P_JWT

    def run(self, args: list[str], stdin: str | None = None) -> str:
        token = stdin or " ".join(args)
        token = token.strip()

        if not token:
            return "Usage: echo 'eyJhbGciOiJIUzI1NiIs...' | devtool jwt decode"

        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        parts = token.split(".")
        if len(parts) < 2:
            return "Error: invalid JWT format (expected 2-3 dot-separated parts)"

        result = []

        try:
            header = decode_jwt_part(parts[0])
            result.append("── Header ──")
            result.append(json.dumps(header, indent=2))
        except Exception as e:
            result.append(f"Header decode error: {e}")

        result.append("")

        try:
            payload = decode_jwt_part(parts[1])
            result.append("── Payload ──")
            result.append(json.dumps(payload, indent=2))

            # Show standard claims
            claims_info = []
            if "exp" in payload:
                from datetime import datetime
                exp_time = datetime.fromtimestamp(payload["exp"])
                claims_info.append(f"  Expires: {exp_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if "iat" in payload:
                iat_time = datetime.fromtimestamp(payload["iat"])
                claims_info.append(f"  Issued:  {iat_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if "sub" in payload:
                claims_info.append(f"  Subject: {payload['sub']}")
            if "iss" in payload:
                claims_info.append(f"  Issuer:  {payload['iss']}")
            if claims_info:
                result.append("")
                result.append("── Claims ──")
                result.extend(claims_info)

        except Exception as e:
            result.append(f"Payload decode error: {e}")

        result.append("")

        if len(parts) >= 3 and parts[2]:
            result.append(f"── Signature ──")
            result.append(f"  Present (not verified) — {len(parts[2])} base64 chars")

        return "\n".join(result)

    def web_render(self) -> str:
        return """<div class="tool-content">
  <h2>JWT Decoder</h2>
  <textarea id="jwt-input" rows="4" placeholder="Paste JWT token..." style="width:100%;font-family:monospace;font-size:13px"></textarea>
  <button onclick="decodeJWT()">Decode</button>
  <div class="tool-output">
    <pre id="jwt-output" class="code-output"></pre>
  </div>
  <script>
    function decodeJWT() {
      fetch('/api/jwt',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({token:document.getElementById('jwt-input').value})
      }).then(r=>r.text()).then(t=>document.getElementById('jwt-output').textContent=t);
    }
  </script>
</div>"""


TOOL = JWTTool()
