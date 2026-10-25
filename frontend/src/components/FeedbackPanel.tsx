import type { Feedback } from "../types";

interface FeedbackPanelProps {
  feedback: Feedback[];
}

export function FeedbackPanel({ feedback }: FeedbackPanelProps) {
  return (
    <section className="panel" aria-labelledby="feedback-title">
      <p className="eyebrow">03 / LEARN</p>
      <h2 id="feedback-title">
        Saved corrections <span className="count">{feedback.length}</span>
      </h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Notification</th>
              <th scope="col">Corrected to</th>
            </tr>
          </thead>
          <tbody>
            {feedback.length ? (
              feedback.map((item, index) => (
                <tr key={`${item.notificationText}-${index}`}>
                  <td>{item.notificationText}</td>
                  <td>
                    {item.correctedCategory} / {item.correctedImportance}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="empty-state" colSpan={2}>
                  No corrections yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <p className="help-text">
        Corrections are saved as feedback for retraining. Training is run by
        separate Python scripts, not by the frontend.
      </p>
    </section>
  );
}
