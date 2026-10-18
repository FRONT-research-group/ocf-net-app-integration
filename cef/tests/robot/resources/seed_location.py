#!/usr/bin/env python3

import argparse
import subprocess
import sys


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--container",
        default="cef-nef-mongo"
    )

    parser.add_argument(
        "--imsi",
        default="001010143245445"
    )

    parser.add_argument(
        "--msisdn",
        default="306912345678"
    )

    args = parser.parse_args()

    javascript = f'''
db.location_info.updateOne(
  {{ _id: "{args.imsi}" }},
  {{
    $set: {{
      UELocationTimestamp: "2025-06-23T20:47:22.000000",
      cellId: "000000010",
      trackingAreaId: "TA-GREECE-002",
      enodeBId: "ENB-PIREAS-010",
      routingAreaId: "RA-CENTRAL-ATH",
      plmnId: {{
        mcc: "202",
        mnc: "01"
      }},
      twanId: null,
      msisdn: "{args.msisdn}",
      monitoringType: "LOCATION_REPORTING"
    }}
  }},
  {{ upsert: true }}
);

printjson(
  db.location_info.findOne(
    {{ _id: "{args.imsi}" }}
  )
);
'''

    result = subprocess.run(
        [
            "docker",
            "exec",
            args.container,
            "mongo",
            "amf_logs",
            "--quiet",
            "--eval",
            javascript
        ],
        text=True,
        capture_output=True
    )

    print(result.stdout, end="")

    if result.stderr:
        print(
            result.stderr,
            end="",
            file=sys.stderr
        )

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
