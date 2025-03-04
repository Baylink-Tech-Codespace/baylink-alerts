
get_wa_alert_template = lambda to , msg : {
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": to,
  "type": "template",
  "template": {
    "name": "beat_plan_notification",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "parameter_name": "fe_name",
            "text": "Karan"
          },
          {
            "type": "text",
            "parameter_name": "retailer_name",
            "text": "Aman Testing"
          },
          {
            "type": "text",
            "parameter_name": "pc",
            "text": ":white_check_mark:"
          },
          {
            "type": "text",
            "parameter_name": "recon",
            "text": ":x:"
          },
          {
            "type": "text",
            "parameter_name": "order",
            "text": ":white_check_mark:"
          },
          {
            "type": "text",
            "parameter_name": "cn",
            "text": ":x:"
          },
          {
            "type": "text",
            "parameter_name": "note",
            "text": msg
          }
        ]
      }
    ]
  }
}