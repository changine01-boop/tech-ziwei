import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — Tech Zi Wei",
};

export default function TermsPage() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1>Terms of Service</h1>
      <p className="text-slate-500 text-sm">Last updated: May 22, 2026</p>

      <p>
        Please read these Terms of Service (&quot;Terms&quot;) carefully before using the Tech Zi
        Wei platform. By creating an account or using our services, you agree to be bound by these
        Terms.
      </p>

      <h2>1. Description of Service</h2>
      <p>
        Tech Zi Wei provides a web-based platform that calculates Zi Wei Dou Shu (紫微斗數)
        astrological charts from birth data and generates AI-powered psychological narrative
        reports framed in modern Western psychological language. The service is provided &quot;as
        is&quot; for self-reflection and entertainment purposes.
      </p>

      <h2>2. Eligibility</h2>
      <p>
        You must be at least 13 years old to use this service. By registering, you represent
        that you meet this age requirement and that the information you provide is accurate.
      </p>

      <h2>3. User Accounts</h2>
      <ul>
        <li>You are responsible for maintaining the confidentiality of your password.</li>
        <li>You are responsible for all activity that occurs under your account.</li>
        <li>Notify us immediately at{" "}
          <a href="mailto:support@techziwei.com">support@techziwei.com</a> if you suspect
          unauthorised access.
        </li>
        <li>We reserve the right to suspend or terminate accounts that violate these Terms.</li>
      </ul>

      <h2>4. Payments</h2>
      <p>
        Certain features (AI-generated readings, PDF export) require a one-time payment of
        <strong> USD $9.99</strong>. All payments are processed securely by Stripe, Inc.
      </p>
      <ul>
        <li>Prices are shown in US dollars and are subject to applicable taxes.</li>
        <li>Payment is charged at the time of checkout.</li>
        <li>
          Access is granted to the account that completed payment and covers all charts created
          by that account going forward.
        </li>
        <li>We do not store your payment card details.</li>
      </ul>

      <h2>5. Refund Policy</h2>
      <p>
        Because the service delivers digital content that is immediately accessible upon payment,
        all sales are <strong>final and non-refundable</strong> except where required by applicable
        law. If you experience a technical failure that prevents you from accessing paid content,
        contact{" "}
        <a href="mailto:support@techziwei.com">support@techziwei.com</a> within 7 days and we
        will work to resolve the issue or, at our discretion, issue a refund.
      </p>

      <h2>6. Acceptable Use</h2>
      <p>You agree not to:</p>
      <ul>
        <li>Use automated tools, bots, or scripts to scrape or abuse the service</li>
        <li>Attempt to reverse-engineer, decompile, or extract the underlying algorithms</li>
        <li>Submit false, misleading, or harmful content</li>
        <li>Use the service to harass, harm, or deceive others</li>
        <li>Circumvent rate limits, authentication, or access controls</li>
        <li>Resell or redistribute generated reports without our written permission</li>
      </ul>

      <h2>7. Intellectual Property</h2>
      <p>
        All software, algorithms, prompts, UI design, and branding on this platform are owned by
        Tech Zi Wei or its licensors. You retain ownership of the birth data you submit. Generated
        reports are licensed to you for personal, non-commercial use only.
      </p>

      <h2>8. Disclaimer of Warranties</h2>
      <p>
        THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
        INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
        NON-INFRINGEMENT. We do not warrant that the service will be uninterrupted, error-free,
        or that chart calculations will be 100% accurate for all birth dates and times.
      </p>

      <h2>9. Limitation of Liability</h2>
      <p>
        TO THE MAXIMUM EXTENT PERMITTED BY LAW, TECH ZI WEI WILL NOT BE LIABLE FOR ANY INDIRECT,
        INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR
        REVENUES, ARISING OUT OF YOUR USE OF THE SERVICE, EVEN IF ADVISED OF THE POSSIBILITY OF
        SUCH DAMAGES. OUR TOTAL LIABILITY TO YOU FOR ANY CLAIMS ARISING OUT OF THESE TERMS OR THE
        SERVICE WILL NOT EXCEED THE AMOUNT YOU PAID US IN THE TWELVE MONTHS PRECEDING THE CLAIM.
      </p>

      <h2>10. Governing Law</h2>
      <p>
        These Terms are governed by and construed in accordance with the laws of the State of
        California, USA, without regard to its conflict of law provisions. Any disputes will be
        resolved in the courts located in California.
      </p>

      <h2>11. Changes to These Terms</h2>
      <p>
        We reserve the right to modify these Terms at any time. We will provide at least 14
        days&apos; notice of material changes by posting the updated Terms with a revised
        &quot;Last updated&quot; date. Continued use of the service after the effective date
        constitutes acceptance.
      </p>

      <h2>12. Contact</h2>
      <p>
        Questions about these Terms?{" "}
        <a href="mailto:legal@techziwei.com">legal@techziwei.com</a>
      </p>
    </article>
  );
}
