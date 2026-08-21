from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv
load_dotenv()


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


HEAD_CONTENT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Action requise - Confirmation de votre réservation de salle</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 20px 0;
            color: #333333;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }
        .header {
            background-color: #b91c1c;
            color: #ffffff;
            padding: 25px 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .content {
            padding: 30px 25px;
        }
        .greeting {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #1e293b;
        }
        .intro {
            font-size: 15px;
            line-height: 1.6;
            color: #475569;
            margin-bottom: 20px;
        }
        .alert-box {
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            border-left: 4px solid #ef4444;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 25px;
            color: #991b1b;
            font-size: 14px;
            line-height: 1.5;
        }
        .alert-box strong {
            color: #7f1d1d;
        }
        .details-box {
            background-color: #f8fafc;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .details-title {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #d97706;
            font-weight: 700;
            margin-bottom: 12px;
        }
        .badge-pending {
            display: inline-block;
            background-color: #fef3c7;
            color: #92400e;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .button-container {
            text-align: center;
            margin: 30px 0;
        }
        .btn-confirm {
            background-color: #16a34a;
            color: #ffffff;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 15px;
            display: inline-block;
            box-shadow: 0 2px 5px rgba(22, 163, 74, 0.3);
        }
        .btn-cancel {
            background-color: transparent;
            color: #64748b;
            text-decoration: underline;
            padding: 8px 16px;
            font-size: 13px;
            display: inline-block;
            margin-top: 10px;
        }
        .footer {
            background-color: #f1f5f9;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>
"""


async def send_email(receiver: str, destinataire: str, date_limite: str, salle: str, date_res: str, heure_debut: str, heure_fin: str):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Rappel de confirmation: Réservation salle."
    message["FROM"] = EMAIL_SENDER
    message["TO"] = receiver

    BODY_CONTENT = HEAD_CONTENT + f"""
<body>
    <div class="container">
        <!-- En-tête -->
        <div class="header">
            <h1>Rappel : Action requise pour votre réservation</h1>
        </div>

        <!-- Corps du message -->
        <div class="content">
            <div class="greeting">Bonjour {destinataire},</div>
            
            <p class="intro">
                Vous avez effectué une pré-réservation pour une salle chez nous. Votre demande est actuellement <strong>en attente de confirmation</strong>.
            </p>

            <!-- Avertissement Annulation -->
            <div class="alert-box">
                <strong>Attention :</strong> Veuillez confirmer votre présence avant le <strong>{date_limite}</strong>. Passé ce délai, votre réservation sera <strong>automatiquement annulée</strong> et la salle sera remise à disposition.
            </div>

            <!-- Récapitulatif -->
            <div class="details-box">
                <div class="details-title">Récapitulatif de la réservation</div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #334155; width: 40%;">Statut actuel :</td>
                        <td style="padding: 6px 0;"><span class="badge-pending">En attente de confirmation</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #334155;">Salle :</td>
                        <td style="padding: 6px 0; color: #0f172a;"><strong>{salle}</strong> (Étage [X])</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #334155;">Date :</td>
                        <td style="padding: 6px 0; color: #0f172a;">{date_res}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #334155;">Horaire :</td>
                        <td style="padding: 6px 0; color: #0f172a;">De {heure_debut} à {heure_fin}</td>
                    </tr>
                </table>
            </div>

            <!-- Bouton d'action -->
            <div class="button-container">
                <a href="[Lien_Confirmation_Reservation]" class="btn-confirm">Confirmer ma réservation</a>
                <br>
                <a href="[Lien_Annulation_Reservation]" class="btn-cancel">Annuler la demande</a>
            </div>

            <p class="intro" style="margin-bottom: 0; font-size: 13px; text-align: center; color: #94a3b8;">
                Si vous avez déjà confirmé entre-temps, veuillez ignorer ce message.
            </p>
        </div>

        <!-- Pied de page -->
        <div class="footer">
            <p style="margin: 0 0 8px 0;">Cet email a été envoyé automatiquement par le système de gestion des salles.</p>
            <p style="margin: 0;">© {datetime.year} — Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""
    message.attach(MIMEText(BODY_CONTENT, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Sécurisation de la connexion via TLS
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, receiver, message.as_string())
        return "OK"
    except Exception as e:
        return e


