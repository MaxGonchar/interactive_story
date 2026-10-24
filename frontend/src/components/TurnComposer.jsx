import { inputBase } from '../styles'
import ModelSelect from './ModelSelect'
import ResponseTimeIndicator from './ResponseTimeIndicator'

export const PLAYER_ACTOR = 'player'

function TurnComposer({
  actor,
  onActorChange,
  characters,
  text,
  onTextChange,
  models,
  characterModelId,
  onCharacterModelChange,
  onSubmit,
  retrying = false,
  onCancelRetry,
  sending = false,
  disabled = false,
  leadingAction = null,
}) {
  const isPlayer = actor === PLAYER_ACTOR
  const canSubmit = !disabled && !sending && (!isPlayer || text.trim() !== '')
  const progressVerb = isPlayer ? 'Narrator is writing' : 'Character and narrator are working'

  return (
    <div className="turn-composer" role="group" aria-label="Turn composer">
      {retrying && (
        <p className="turn-composer__retry-status" role="status">
          Retrying last paragraph
        </p>
      )}
      <div className="turn-composer__selects">
        <label htmlFor="turn-actor" className="new-scene-page__field">
          <span className="new-scene-page__label">Actor</span>
          <select
            id="turn-actor"
            className="form-control__select"
            value={actor}
            onChange={(event) => onActorChange(event.target.value)}
            disabled={disabled || sending}
          >
            <option value={PLAYER_ACTOR}>Player</option>
            {characters.map((character) => (
              <option key={character.id} value={character.id}>{character.name}</option>
            ))}
          </select>
        </label>
        <ModelSelect
          id="turn-character-model"
          label="Character LLM"
          models={models}
          value={characterModelId ?? ''}
          onChange={onCharacterModelChange}
          disabled={disabled || sending || isPlayer}
        />
      </div>
      <textarea
        className="turn-composer__textarea"
        aria-label={isPlayer ? 'Action' : 'Guidance'}
        value={text}
        onChange={(event) => onTextChange(event.target.value)}
        disabled={disabled || sending}
        placeholder={isPlayer ? 'What do you do?' : 'Optional guidance for the character…'}
        style={inputBase}
      />
      <div className="turn-composer__actions">
        {leadingAction}
        {retrying && (
          <button
            onClick={onCancelRetry}
            disabled={sending}
            type="button"
          >
            Cancel retry
          </button>
        )}
        {sending && <ResponseTimeIndicator verb={progressVerb} />}
        <button
          className="turn-composer__submit"
          onClick={onSubmit}
          disabled={!canSubmit}
        >
          {retrying ? 'Replace last paragraph' : isPlayer ? 'Send' : 'Trigger'}
        </button>
      </div>
    </div>
  )
}

export default TurnComposer
