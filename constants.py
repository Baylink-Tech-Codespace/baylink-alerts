SWIPE_DOC_API_URL = "https://app.getswipe.in/api/partner/v2/doc/list"

SWIPE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxNTc4NDUxLCJuYW1lIjoiQVBJIFVzZXIiLCJjb21wYW55X2lkIjoxMjM4MjMzLCJjb21wYW55X25hbWUiOiJCQVlMSU5LIEJVU0lORVNTIFBSSVZBVEUgTElNSVRFRCIsInBhcnRuZXIiOnRydWUsImlhdCI6MTczNDA4NzAwMCwidmVyc2lvbiI6Mn0.8fFOmBgMZMmv6b4-lEWpOFTGsdGvBMhhmnkXM12c5gs"

get_wa_alert_template = lambda to, msg : {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "91" + to,
    "type": "template",
    "template": {
      "name": "baylink_task_notify",
      "language": {
        "code": "en"
      },
      "components": [
        {
          "type": "body",
          "parameters": [
            {
              "type": "text",
              "parameter_name": "task_message",
              "text": msg
            }
          ]
        }
      ]
    }
}