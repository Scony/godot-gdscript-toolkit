;;;
;;; gdformat.el --- Reformat GDScript buffers using the "gdformat" formatter
;;;
;;; This module is a part of gdtoolkit, see https://github.com/Scony/godot-gdscript-toolkit
;;;

(defun gdformat-call-bin (input-buffer output-buffer error-buffer)
  "Call gdformat process"
  (with-current-buffer input-buffer
    (let ((process (make-process :name "gdformat"
                                 :command (list "python" "-m" "gdtoolkit.formatter" "-")
                                 :buffer output-buffer
                                 :stderr error-buffer
                                 :noquery t
                                 :sentinel (lambda (process event)))))
      (set-process-query-on-exit-flag (get-buffer-process error-buffer) nil)
      (set-process-sentinel (get-buffer-process error-buffer) (lambda (process event)))
      (save-restriction
        (widen)
        (process-send-region process (point-min) (point-max)))
      (process-send-eof process)
      (accept-process-output process nil nil t)
      (while (process-live-p process)
        (accept-process-output process nil nil t))
      (process-exit-status process)
      )
    )
  )

(defun gdformat-buffer ()
  "Formats current buffer using 'gdformat'"
  (interactive)
  (let* ((original-buffer (current-buffer))
         (original-point (point))
         (original-window-pos (window-start))
         (tmpbuf (get-buffer-create "*gdformat*"))
         (errbuf (get-buffer-create "*gdformat-error*")))
    (dolist (buf (list tmpbuf errbuf))
      (with-current-buffer buf (erase-buffer)))
    (condition-case err
        (if (not (zerop (gdformat-call-bin original-buffer tmpbuf errbuf)))
            (error "gdformat: failed, see %s buffer for details" (buffer-name errbuf))
          (if (not (eq (compare-buffer-substrings tmpbuf nil nil original-buffer nil nil) 0))
              (progn
                (with-current-buffer tmpbuf
                  (copy-to-buffer original-buffer (point-min) (point-max)))
                (goto-char original-point)
                (set-window-start (selected-window) original-window-pos)
                (message "gdformat: success")
                )
            (message "gdformat: nothing to do")
            )
          (mapc 'kill-buffer (list tmpbuf errbuf))
          )
      (error (message "%s" (error-message-string err))
             (pop-to-buffer errbuf)
             )
      )
    )
  )

(provide 'gdformat)
